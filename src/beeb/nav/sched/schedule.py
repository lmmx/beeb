import requests
import re
from bs4 import BeautifulSoup as BS
from ..channel_ids import ChannelPicker
from ...time import parse_abs_from_rel_date, cal_path
from datetime import datetime

__all__ = ["Schedule"]


class Schedule:
    """
    Schedule for the channel specified by ID in the init method or using
    the constructor classmethod `from_channel_name` which retrieves the channel
    ID from a string (the shortname given in `beeb.nav.channel_ids`).

    The contents of a Schedule is the schedule listings for a single day,
    and the date can be specified as a datetime object `date`. The
    `base_url` gives the current day's schedule, and adding date subpaths
    onto it gives a calendar view (for just the year or year and month),
    which are only useful for indicating the furthest ahead available listings,
    since we can generate the calendar offline in Python,
    or individual listings (for a full date).

    BBC schedules have redundant entries after midnight, so these are dropped
    (they should be loaded from that day's entries instead).
    """

    common_url_prefix = "https://www.bbc.co.uk/schedules/"

    @property
    def channel(self):
        return ChannelPicker.by_id(self.channel_id)

    def __init__(self, channel_id, date=None):
        self.channel_id = channel_id
        self.date = date
        try:
            self.channel
        except Exception as e:
            raise e  # channel ID is invalid, don't accept
        self.base_url = f"{self.common_url_prefix}{self.channel_id}"
        self.parse_schedule()

    @property
    def date_repr(self):
        if self.date:
            return self.date.strftime("%d/%m/%Y")

    @property
    def ymd(self):
        return (self.date.year, self.date.month, self.date.day)

    @classmethod
    def from_channel_name(cls, name, date=None):
        channel = ChannelPicker.by_name(name, must_exist=True)
        return cls(channel.channel_id, date=date)

    def parse_schedule(self, drop_next_day_broadcasts=True):
        if self.date is None:
            self.date = parse_abs_from_rel_date()
        ymd_path = "/".join(cal_path(self.date, as_tuple=True)) if self.date else None
        sched_url = f"{self.base_url}{'/' + ymd_path if self.date else ''}"
        r = requests.get(sched_url)
        r.raise_for_status()
        self.soup = BS(r.content.decode(), features="html5lib")
        self.broadcasts = [
            Broadcast.from_soup(b) for b in self.soup.select(".broadcast")
        ]
        if drop_next_day_broadcasts:
            self.broadcasts = [
                b for b in self.broadcasts
                if (b.time.year, b.time.month, b.time.day) == self.ymd
            ]

    def __repr__(self):
        return f"Schedule for {self.channel.title} on {self.date}"

    def get_broadcast_by_title(
        self, title, pid_only=False, multi=False, regex=False, case_insensitive=False,
        synopsis=False, throw=True
    ):
        """
        Return the first broadcasts matching the given `title` if `multi` is
        False (default) or a list of all matches if `multi` is True. Return
        only the `pid` string if `pid_only` is True. If `throw` is True (default),
        raise error if not found else return `None` (if not `multi`) or empty list
        (if `multi` is True). Match the `title` as a regular expression if `regex` is
        True (raw strings are recommended for this). Also match against the subtitle
        and synopsis if `synopsis` is True.
        """
        if regex:
            if case_insensitive:
                rc = re.compile(title, re.IGNORECASE)
            else:
                rc = re.compile(title)
        is_match = rc.match if regex else title.__eq__ # re.Match object is truthy
        v = [
            b.pid if pid_only else b for b in self.broadcasts
            if any(
                is_match(t)
                for t in ([b.title, b.subtitle, b.synopsis] if synopsis else [b.title])
            )
        ]
        if not v:
            if throw:
                raise ValueError(f"No broadcast {title} on {self.date_repr}")
            elif not multi:
                v = None
        elif not multi:
            v = v[0]
        return v


class Broadcast:
    def __init__(self, dt, pid, title, subtitle, synopsis):
        self.time = dt
        self.pid = pid
        self.title = title
        self.subtitle = subtitle
        self.synopsis = synopsis

    @classmethod
    def from_soup(cls, bsoup):
        """
        Parse a `div.broadcast` HTML tag in BeautifulSoup.
        """
        pid = bsoup.select_one("*[data-pid]")
        title = bsoup.select_one(".programme__titles .programme__title")
        subtitle = bsoup.select_one(".programme__titles .programme__subtitle")
        synopsis = bsoup.select_one(".programme__body .programme__synopsis span")
        text_tags = title, subtitle, synopsis
        dt = bsoup.select_one("h3.broadcast__time[content]")
        if not all([pid, dt, *text_tags]):
            raise ValueError(
                f"Missing one or more of: "
                f"{pid=} {title=} {subtitle=}, {synopsis=}"
            )
        title, subtitle, synopsis = [x.text for x in text_tags]
        pid = pid.attrs["data-pid"]
        dt = datetime.fromisoformat(dt.attrs["content"])
        return cls(dt, pid, title, subtitle, synopsis)

    @property
    def date_repr(self):
        return self.time.strftime("%d/%m/%Y")

    @property
    def time_repr(self):
        return self.time.strftime("%H:%M")

    def __repr__(self):
        return f"{self.time_repr} on {self.date_repr} — {self.title}"
