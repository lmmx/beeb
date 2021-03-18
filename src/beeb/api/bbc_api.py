from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup as BS
from json import loads
import httpx
from ..time.isotime import total_seconds_in_isoduration
from math import ceil

__all__ = [
    "get_episode_dict",
    "final_m4s_link_from_series_pid",
    "final_m4s_link_from_episode_pid",
]


def get_episode_dict(series_pid, page_num=1, paginate_until_ymd=None):
    """
    Return a dict of (year, month, day) tuple keys to episode PID values for
    the given page number. Raise an error if anything whatsoever goes wrong.

    Check all available dates until matching the (year, month, day) tuple
    if provided as `paginate_until_ymd` (note year must be full year),
    and upon doing so remove all other keys and return the singleton dict.
    """
    # TODO: extend this to return all episode dates and PIDs if that's desirable
    url_prefix = f"https://www.bbc.co.uk/programmes/{series_pid}/episodes/player?page="
    url = f"{url_prefix}{page_num}"
    episodes_resp = httpx.get(url)
    episodes_resp.raise_for_status()
    soup = BS(episodes_resp.content.decode(), features="html5lib")
    episoup = soup.select("div[data-pid]")
    if paginate_until_ymd:
        # Given a date ymd tuple, iterate page_num to the maximum and/or until ymd found
        max_page_num = int(soup.select_one(".pagination__page--last").a.text)
    else:
        max_page_num = page_num
    episodes_dict = {}
    if episoup:
        for epinode in episoup:
            episode_pid = epinode.attrs["data-pid"]
            episode_title = epinode.select_one(".programme__titles").text
            try:
                epi_d, epi_m, epi_y = map(int, episode_title.split("/"))
                epi_ymd = (epi_y, epi_m, epi_d)
            except Exception as e:
                raise ValueError(f"Failed to parse {episode_title=} as a date")
            episodes_dict.update({epi_ymd: episode_pid})
    else:
        raise ValueError(f"No episodes found at {url=}")
    if paginate_until_ymd and paginate_until_ymd not in episodes_dict:
        # cover the rest of the pages up to and including `max_page_num`
        for paginate in range(page_num + 1, max_page_num + 1):
            paginate_ep_dict = get_episode_dict(series_pid, paginate)
            # TODO conditional update here if returning all
            episodes_dict.update(paginate_ep_dict)
            if paginate_until_ymd in episodes_dict:
                # Clear all other entries and break to return the singleton dict
                episodes_dict = {paginate_until_ymd: episodes_dict[paginate_until_ymd]}
                break
            if page_num == max_page_num:
                raise ValueError(f"{paginate_until_ymd} not found (reached {page_num})")
    elif paginate_until_ymd:
        episodes_dict = {paginate_until_ymd: episodes_dict[paginate_until_ymd]}
    return episodes_dict


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
    last_m4s_link = final_m4s_link_from_episode_pid(episode_pid)
    return last_m4s_link


def final_m4s_link_from_episode_pid(episode_pid):
    """
    Scrape the DASH manifest (MPD file) to determine the URL of the final M4S file
    (MPEG stream), using the episode's duration divided by the... sampling rate?
    """
    verpid = episode_pid
    pid_json_url = f"https://www.bbc.co.uk/programmes/{episode_pid}/playlist.json"
    pid_json_resp = httpx.get(pid_json_url)
    pid_json_resp.raise_for_status()
    pid_json = loads(pid_json_resp.content.decode())
    verpid = pid_json["defaultAvailableVersion"]["pid"]
    mediaset_v = 6
    mediaset_url = (
        f"https://open.live.bbc.co.uk/mediaselector/{mediaset_v}/"
        f"select/version/2.0/mediaset/pc/vpid/{verpid}"
    )
    mediaset_resp = httpx.get(mediaset_url)
    mediaset_resp.raise_for_status()
    mediaset_json = loads(mediaset_resp.content.decode())
    if mediaset_json.get("result") == "selectionunavailable":
        raise ValueError(f"Bad mediaset response from {episode_pid}")
    # `sorted()[0]` with the key 'priority' gives 'top' choice of 3 suppliers
    mpd_url = sorted(
        [
            x
            for x in mediaset_json["media"][0]["connection"]
            if x["transferFormat"] == "dash"
            if x["protocol"] == "https"
        ],
        key=lambda e: int(e["priority"]),
    )[0]["href"]
    mpd_resp = httpx.get(mpd_url)
    mpd_resp.raise_for_status()
    mpd_resp_xml = ET.fromstring(mpd_resp.content.decode())
    duration_string = mpd_resp_xml.get("mediaPresentationDuration")
    sec_duration = total_seconds_in_isoduration(duration_string)
    # Choose the highest bitrate option (there are 2 AdaptationSet options)
    xsd_namespace = mpd_resp_xml.items()[0][1].split()[0]
    ns_xpath = f"{{{xsd_namespace}}}"
    # Assume a single period duration (so use `find` not `findall`)
    period_xpath = f"{ns_xpath}Period"
    bitrate_opt_xpath = f"{ns_xpath}AdaptationSet"
    repr_xpath = f"{ns_xpath}Representation"
    max_bitrate_opt = sorted(
        mpd_resp_xml.find(period_xpath).findall(bitrate_opt_xpath),
        key=lambda t: int(t.find(repr_xpath).get("bandwidth")),
    )[
        -1
    ]  # take the maximum value, the last in the sorted list
    seg_templ_xpath = f"{ns_xpath}SegmentTemplate"
    segment_frames = int(max_bitrate_opt.find(seg_templ_xpath).get("duration"))
    sample_rate = int(max_bitrate_opt.get("audioSamplingRate"))
    n_m4s_parts = ceil(sec_duration * sample_rate / segment_frames)
    base_url_xpath = f"{ns_xpath}BaseURL"
    mpd_base_url = mpd_resp_xml.find(period_xpath).find(base_url_xpath).text
    segment_frames = int(max_bitrate_opt.find(seg_templ_xpath).get("duration"))
    repr_id = max_bitrate_opt.find(repr_xpath).get("id")
    media_url_suff = max_bitrate_opt.find(seg_templ_xpath).get("media")
    media_suff_parts = media_url_suff.split("$")
    media_suff_parts[1::2] = repr_id, str(n_m4s_parts)
    m4s_link_prefix = mpd_url[: mpd_url.rfind("/") + 1]
    last_m4s_suffix = "".join(media_suff_parts)
    last_m4s_link = m4s_link_prefix + mpd_base_url + last_m4s_suffix
    return last_m4s_link
