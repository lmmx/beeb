from .serialisation import JsonHandler

__all__ = ["EpisodePidJson", "MediasetJson"]


class EpisodePidJson(JsonHandler):
    "Episode metadata JSON helper"
    pid_property_name = "episode_pid"

    @property
    def url(self):
        return f"https://www.bbc.co.uk/programmes/{self.episode_pid}/playlist.json"


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
        vpid = EpisodePidJson(episode_pid, filter_key_path=vpid_key_path).filtered
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
