from bs4 import BeautifulSoup as BS
from math import ceil
from ..share.time.isotime import total_seconds_in_isoduration
from .serialisation import HtmlHandler

# TODO make this file into a HTML helper version supported by .serialisation

__all__ = ["EpisodeListingsHtml"]


class Series:
    base_url = "https://www.bbc.co.uk/programmes/"

    def __init__(self, series_pid):
        self.pid = series_pid

    @property
    def url(self):
        return f"{self.base_url}{self.pid}"


class Paginator:
    # TODO: extend this to return all episode dates and PIDs if that's desirable?
    start_page_num = 1
    current_page_num = start_page_num

    def reset_paginator(self, start_page_num=None):
        if self.start_page_num is start_page_num is self.current_page_num:
            pass  # Nothing to do
        else:
            if start_page_num is not None:
                self.start_page_num = start_page_num
            self.current_page_num = self.start_page_num

    def paginate(self):
        self.current_page_num += 1

    def set_paginate_ymd_limit(self, paginate_until_ymd=None):
        """
        Set the (year, month, day) integer tuple, where year is full year,
        representing the 'end goal' upon finding which pagination will stop.
        """
        self._pg_ymd_lim = paginate_until_ymd

    @property
    def paginate_until_ymd(self):
        return self._pg_ymd_lim


class Episode:
    def __init__(self, pid, title, ymd):
        self.pid = pid
        self.title = title
        self.ymd = ymd

    @classmethod
    def from_soup_node(cls, soup_node):
        pid = soup_node.attrs["data-pid"]
        episode_title = soup_node.select_one(".programme__titles").text
        try:
            epi_d, epi_m, epi_y = map(int, episode_title.split("/"))
            epi_ymd = (epi_y, epi_m, epi_d)
        except Exception as e:
            raise ValueError(f"Failed to parse {episode_title=} as a date")
        return cls(pid=pid, title=episode_title, ymd=epi_ymd)


class EpisodesDict(dict):
    """
    dict of (year, month, day) tuple keys to episode PID values for
    the given page number. Raise an error if anything whatsoever goes wrong.

    Check all available dates until matching the (year, month, day) tuple
    if provided as `paginate_until_ymd` (note year must be full year),
    and upon doing so remove all other keys and return the singleton dict.

    Note: without a `paginate_until_ymd` value, the dict for a single page
    will be returned (this is by design, avoiding recursive pagination).
    """

    def __init__(
        self,
        episode_soups,
        series_pid,
        max_page_num,
        start_page_num=1,
        paginate_until_ymd=None,
    ):
        self.series_pid = series_pid
        self.start_page_num = start_page_num
        self.max_page_num = max_page_num
        self.paginate_until_ymd = paginate_until_ymd
        self.parse_soups(episode_soups)

    def parse_soups(self, episode_soups):
        if episode_soups:
            for epinode in episode_soups:
                e = Episode.from_soup_node(epinode)
                self.update({e.ymd: e.pid})
        else:
            raise ValueError(f"No episodes found at {url=}")
        if self.paginate_until_ymd and self.paginate_until_ymd not in self:
            # cover the rest of the pages up to and including `max_page_num`
            for paginate in range(self.start_page_num + 1, self.max_page_num + 1):
                paginate_ep_dict = EpisodeListingsHtml(
                    series_pid=self.series_pid, page_num=paginate
                ).episodes_dict
                # TODO conditional update here if returning all
                self.update(paginate_ep_dict)
                if self.paginate_until_ymd in self:
                    # Clear all other entries and break to return the singleton dict
                    self.prune(self.paginate_until_ymd)
                    break
                if paginate == self.max_page_num:
                    msg = f"{self.paginate_until_ymd} not found (reached {page_num})"
                    raise ValueError(msg)
        elif self.paginate_until_ymd:
            self.prune(self.paginate_until_ymd)

    def prune(self, k):
        "Delete all dict keys except the singleton entry for a given key, `k`."
        if k not in self:
            raise KeyError("Cannot prune on this key: {k=}")
        singleton_dict = {k: self[k]}
        self.clear()
        self.update(singleton_dict)

    @classmethod
    def from_episode_listings(cls, ep_lst):
        return cls(
            episode_soups=ep_lst.episode_soups,
            series_pid=ep_lst.series.pid,
            max_page_num=ep_lst.max_page_num,
            start_page_num=ep_lst.start_page_num,
            paginate_until_ymd=ep_lst.paginate_until_ymd,
        )


class EpisodeListingsHtml(Paginator, HtmlHandler):
    def __init__(
        self, series_pid, page_num=1, paginate_until_ymd=None, defer_pull=False
    ):
        self.series = Series(series_pid)
        self.reset_paginator(page_num)  # initialise paginator
        self.set_paginate_ymd_limit(paginate_until_ymd)
        if not defer_pull:
            self.pull()
        self.episodes_dict = EpisodesDict.from_episode_listings(self)

    @property
    def paginate_url_prefix(self):
        return f"{self.series.url}/episodes/player?page="

    @property
    def url(self):
        return f"{self.paginate_url_prefix}{self.current_page_num}"

    @property
    def episode_soups(self):
        return self.page.select("div[data-pid]")

    @property
    def max_page_num(self):
        """
        Given a date ymd tuple, iterate current_page_num to max. and/or until ymd found
        """
        if self.paginate_until_ymd:
            n = int(self.page.select_one(".pagination__page--last").a.text)
        else:
            n = self.current_page_num
        return n

    @property
    def episode_dict(self):
        return self.build_episode_dict()
