from .serialisation import JsonHandler

__all__ = ["EpisodePlaylistPidJson", "EpisodeMetadataPidJson", "MediasetJson"]


class EpisodePlaylistPidJson(JsonHandler):
    "Episode playlist metadata JSON helper"
    pid_property_name = "episode_pid"

    @property
    def url(self):
        return f"https://www.bbc.co.uk/programmes/{self.episode_pid}/playlist.json"

class EpisodeMetadataPidJson(JsonHandler):
    "Episode metadata JSON helper"
    pid_property_name = "episode_pid"
    parent_type_kp = "programme parent programme type".split()
    # Presume only a single parent (brand) unless multiple parents (series and brand)
    programme_pid_kp = "programme parent programme pid".split()
    programme_title_kp = "programme parent programme title".split()
    cat_kp = "programme categories".split() # unkeyed list here
    filter_key_path = programme_pid_kp

    @property
    def url(self):
        return f"https://www.bbc.co.uk/programmes/{self.episode_pid}.json"

    @property
    def parent_type(self):
        return self.filter(self.parent_type_kp, force_preserve=True)

    def detect_parent_is_series(self):
        """
        Check whether the brand is nested beneath the series, and augment keypath
        attributes if so (else parent type is a single 'brand').
        """
        if self.parent_type == "series":
            prog_stem = "programme parent programme parent programme"
            self.programme_pid_kp = f"{prog_stem} pid".split()
            self.programme_title_kp = f"{prog_stem} title".split()

    @classmethod
    def get_programme_pid(cls, episode_pid, prefab=None):
        j = prefab if prefab else cls(episode_pid)
        j.detect_parent_is_series()
        return j.filter(filter_key_path=j.programme_pid_kp)

    @classmethod
    def get_programme_pid_title(cls, episode_pid, prefab=None):
        j = prefab if prefab else cls(episode_pid)
        j.detect_parent_is_series()
        programme_pid_title_kp = (j.programme_pid_kp, j.programme_title_kp)
        return j.filter(filter_key_path=programme_pid_title_kp)

    @classmethod
    def get_programme_pid_title_genre(cls, episode_pid, prefab=None):
        j = prefab if prefab else cls(episode_pid)
        j.detect_parent_is_series() # modify keypath attributes if series
        programme_pid_title_kp = (j.programme_pid_kp, j.programme_title_kp)
        # Force preserve: don't clear the dict
        programme_pid, programme_title = j.filter(
            filter_key_path=programme_pid_title_kp, force_preserve=True
        )
        genre_title = next(
            c["title"]
            for c in j.filter(j.cat_kp) # Don't force preserve: clear the dict
            if c.get("type") == "genre"
        )
        return programme_pid, programme_title, genre_title

class MediasetJson(JsonHandler):
    "MPEG-DASH stream manifest JSON helper"
    pid_property_name = "verpid"
    mediaset_v = 6

    @property
    def url(self):
        return (
            f"https://open.live.bbc.co.uk/mediaselector/{self.mediaset_v}/"
            f"select/version/2.0/mediaset/pc/vpid/{self.verpid}"
        )

    @classmethod
    def from_episode_pid(cls, episode_pid, defer_pull=False, filter_key_path=None):
        vpid_key_path = ["defaultAvailableVersion", "pid"]
        vpid = EpisodePlaylistPidJson(episode_pid, filter_key_path=vpid_key_path).filtered
        try:
            ms_json = cls(vpid, defer_pull=defer_pull, filter_key_path=filter_key_path)
        except KeyError as e:
            # JSON dict not cleared if filtering threw a KeyError
            if ms_json.get("result") == "selectionunavailable":
                raise ValueError(f"Bad mediaset response from {episode_pid}")
            raise e  # Other error types to catch (could wrap/re-throw via base class?)
        return ms_json

    @property
    def mpd_url(self):
        """
        The first MPEG-DASH stream URL sorted by 'priority' is 'top' choice of 3
        suppliers. Choose HTTPS (possibly slower than HTTP but not tested this?)
        """
        return self.sorted_by_priority(https=True)[0]["href"]

    def sorted_by_priority(self, https=True):
        return sorted(
            [
                x
                for x in self["media"][0]["connection"]
                if x["transferFormat"] == "dash"
                if x["protocol"] == f"http{'s' if https else ''}"
            ],
            key=lambda e: int(e["priority"]),
        )
