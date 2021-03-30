from .serialisation import XmlHandler
from .json_helpers import MediasetJson
from ..share.time.isotime import total_seconds_in_isoduration
from math import ceil

__all__ = ["MpdXml"]


class MpdXsdNamespaceMixIn:
    "Helper to parse MPD XML's XSD namespace."

    @property
    def namespace_xpath(self):
        """
        Relies on the `xsd_namespace` property of `MpdXml`, made from the values
        loaded into the dict from the `attrib` dict of `ElementTree.Element`.
        """
        return f"{{{self.xsd_namespace}}}"

    @property
    def period_xpath(self):
        return f"{self.namespace_xpath}Period"

    @property
    def bitrate_opt_xpath(self):
        return f"{self.namespace_xpath}AdaptationSet"

    @property
    def repr_xpath(self):
        return f"{self.namespace_xpath}Representation"

    @property
    def seg_templ_xpath(self):
        return f"{self.namespace_xpath}SegmentTemplate"

    @property
    def base_url_xpath(self):
        return f"{self.namespace_xpath}BaseURL"


class MpdXml(MpdXsdNamespaceMixIn, XmlHandler):
    "Episode stream MPD manifest XML helper"
    duration_key = "mediaPresentationDuration"
    clear_on_filter = False

    @classmethod
    def from_episode_pid(cls, episode_pid, defer_pull=False, filter_key_path=None):
        mediaset_json = MediasetJson.from_episode_pid(
            episode_pid, defer_pull=defer_pull, filter_key_path=filter_key_path
        )
        return cls(mediaset_json.mpd_url)

    @property
    def duration_string(self):
        return self.filter(filter_key_path=[self.duration_key])

    @property
    def sec_duration(self):
        return total_seconds_in_isoduration(self.duration_string)

    @property
    def xsd_namespace(self):
        try:
            ns = next(v for v in self.values()).split(" ")[0]
        except Exception as e:
            raise ValueError("Failed to extract XSD namespace: {e}")
        return ns

    @property
    def max_bitrate_opt(self):
        """
        Choose the highest bitrate option (there are 2 AdaptationSet options).
        Assume a single period duration (so use `find` not `findall`). Take
        the maximum value: the last in the sorted list.
        """
        return self.bitrates_sorted_by_bandwidth()[-1]

    def bitrates_sorted_by_bandwidth(self):
        return sorted(
            self.root.find(self.period_xpath).findall(self.bitrate_opt_xpath),
            key=lambda t: int(t.find(self.repr_xpath).get("bandwidth")),
        )

    @property
    def segment_frames(self):
        return int(self.max_bitrate_opt.find(self.seg_templ_xpath).get("duration"))

    @property
    def sample_rate(self):
        return int(self.max_bitrate_opt.get("audioSamplingRate"))

    @property
    def n_m4s_parts(self):
        return ceil(self.sec_duration * self.sample_rate / self.segment_frames)

    @property
    def mpd_base_url(self):
        return self.root.find(self.period_xpath).find(self.base_url_xpath).text

    @property
    def repr_id(self):
        return self.max_bitrate_opt.find(self.repr_xpath).get("id")

    @property
    def media_url_suffix(self):
        return self.max_bitrate_opt.find(self.seg_templ_xpath).get("media")

    @property
    def m4s_link_prefix(self):
        return self.url[: self.url.rfind("/") + 1]

    @property
    def last_m4s_link(self):
        "Return the final M4S stream link"
        media_suffix_parts = self.media_url_suffix.split("$")
        media_suffix_parts[1::2] = self.repr_id, str(self.n_m4s_parts)
        last_m4s_suffix = "".join(media_suffix_parts)
        return self.m4s_link_prefix + self.mpd_base_url + last_m4s_suffix
