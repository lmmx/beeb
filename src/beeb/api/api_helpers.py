from .xml_helpers import MpdXml
from .html_helpers import EpisodeListingsHtml
from .json_helpers import EpisodeMetadataPidJson
from ..nav.sched import ChannelListings, ProgrammeCatalogue

__all__ = [
    "get_episode_dict",
    "final_m4s_link_from_programme_pid",
    "final_m4s_link_from_episode_pid",
    "get_programme_pid_by_name",
    "get_programme_dict",
    "get_genre_programme_dict"
]


def final_m4s_link_from_episode_pid(episode_pid):
    """
    Scrape the DASH manifest (MPD file) to determine the URL of the final M4S file
    (MPEG stream), using the episode's duration divided by the... sampling rate?
    """
    return MpdXml.from_episode_pid(episode_pid).last_m4s_link


def final_m4s_link_from_programme_pid(programme_pid, ymd):
    """
    Return the final M4S stream link given the programme PID and (year, month, day)
    tuple (looking up all available episodes until one on this date is found).
    Note that the year in `ymd` must be the full year.
    """
    if ymd[0] < 100:
        raise ValueError(f"The year in {ymd=} must be given as the full year.")
    ret_dict = get_episode_dict(programme_pid, paginate_until_ymd=ymd)
    if len(ret_dict) > 1:
        raise ValueError(f"Got {len(ret_dict)} keys for {paginate_until_ymd=}")
    [episode_pid] = ret_dict.values()
    return MpdXml.from_episode_pid(episode_pid).last_m4s_link


def get_episode_dict(programme_pid, page_num=1, paginate_until_ymd=None):
    """
    Return a dict of (year, month, day) tuple keys to episode PID values for
    the given page number. Raise an error if anything whatsoever goes wrong.

    Check all available dates until matching the (year, month, day) tuple
    if provided as `paginate_until_ymd` (note year must be full year),
    and upon doing so remove all other keys and return the singleton dict.
    """
    return EpisodeListingsHtml(programme_pid, page_num, paginate_until_ymd).episodes_dict

def get_programme_pid_by_name(programme_name, station_name, n_days=2):
    """
    Given the name of a programme and a channel, return the PID for the programme.
    """
    listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
    try:
        episode = listings.get_broadcast_by_title(programme_name)
    except ValueError as e:
        msg = f"No programme '{programme_name}' found, try increasing {n_days=}"
        raise NotImplementedError(msg)
    finally:
        programme_pid = EpisodeMetadataPidJson.get_programme_pid(episode.pid)
    return programme_pid

def get_programme_dict(station_name, with_genre=False, n_days=1):
    """
    Given the name of a channel, return a dict of programme PIDs and programme titles.
    If `with_genre` is True, make the value a 2-tuple of (title, genre).
    """
    return ProgrammeCatalogue(station_name, with_genre, n_days)

def get_genre_programme_dict(station_name, n_days=1):
    programme_dict = get_programme_dict(station_name, with_genre=True, n_days=n_days)
    return programme_dict.keyed_by_genre
