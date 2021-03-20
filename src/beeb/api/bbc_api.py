from .xml_helpers import MpdXml
from .html_helpers import EpisodeListingsHtml

__all__ = [
    "get_episode_dict",
    "final_m4s_link_from_series_pid",
    "final_m4s_link_from_episode_pid",
]


def final_m4s_link_from_episode_pid(episode_pid):
    """
    Scrape the DASH manifest (MPD file) to determine the URL of the final M4S file
    (MPEG stream), using the episode's duration divided by the... sampling rate?
    """
    return MpdXml.from_episode_pid(episode_pid).last_m4s_link


def final_m4s_link_from_series_pid(series_pid, ymd):
    """
    Return the final M4S stream link given the series PID and (year, month, day)
    tuple (looking up all available episodes until one on this date is found).
    Note that the year in `ymd` must be the full year.
    """
    if ymd[0] < 100:
        raise ValueError(f"The year in {ymd=} must be given as the full year.")
    ret_dict = get_episode_dict(series_pid, paginate_until_ymd=ymd)
    if len(ret_dict) > 1:
        raise ValueError(f"Got {len(ret_dict)} keys for {paginate_until_ymd=}")
    [episode_pid] = ret_dict.values()
    return MpdXml.from_episode_pid(episode_pid).last_m4s_link


def get_episode_dict(series_pid, page_num=1, paginate_until_ymd=None):
    """
    Return a dict of (year, month, day) tuple keys to episode PID values for
    the given page number. Raise an error if anything whatsoever goes wrong.

    Check all available dates until matching the (year, month, day) tuple
    if provided as `paginate_until_ymd` (note year must be full year),
    and upon doing so remove all other keys and return the singleton dict.
    """
    return EpisodeListingsHtml(series_pid, page_num, paginate_until_ymd).episodes_dict
