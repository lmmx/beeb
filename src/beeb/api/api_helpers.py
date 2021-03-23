from .xml_helpers import MpdXml
from .html_helpers import EpisodeListingsHtml
from .json_helpers import EpisodeMetadataPidJson
from ..nav.sched import ChannelListings, SeriesCatalogue

__all__ = [
    "get_episode_dict",
    "final_m4s_link_from_series_pid",
    "final_m4s_link_from_episode_pid",
    "get_series_pid_by_name",
    "get_series_dict",
    "get_genre_series_dict"
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

def get_series_pid_by_name(series_name, station_name, n_days=2):
    """
    Given the name of a series and a channel, return the PID for the series.
    """
    listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
    try:
        episode = listings.get_broadcast_by_title(series_name)
    except ValueError as e:
        msg = f"No programme '{series_name}' found, try increasing {n_days=}"
        raise NotImplementedError(msg)
    finally:
        series_pid = EpisodeMetadataPidJson.get_series_pid(episode.pid)
    return series_pid

def get_series_dict(station_name, with_genre=False, n_days=1):
    """
    Given the name of a channel, return a dict of series PIDs and series titles.
    If `with_genre` is True, make the value a 2-tuple of (title, genre).
    """
    return SeriesCatalogue(station_name, with_genre, n_days)

def get_genre_series_dict(station_name, n_days=1):
    series_dict = get_series_dict(station_name, with_genre=True, n_days=n_days)
    genre_dict = {}
    for genre_title, series_pid_and_title in (
        [v[1], (k, v[0])]
        for (k,v) in series_dict.items()
    ):
        genre_dict.setdefault(genre_title, [])
        genre_dict[genre_title].append(series_pid_and_title)
    return genre_dict
