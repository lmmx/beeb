import requests
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
            raise e # channel ID is invalid, don't accept
        self.base_url = f"{self.common_url_prefix}{self.channel_id}"
        self.parse_schedule()

    @classmethod
    def from_channel_name(cls, name, date=None):
        channel = ChannelPicker.by_name(name, must_exist=True)
        return cls(channel.channel_id, date=date)

    def parse_schedule(self):
        if self.date is None:
            self.date = parse_abs_from_rel_date()
        ymd_path = "/".join(cal_path(self.date, as_tuple=True)) if self.date else None
        sched_url = f"{self.base_url}{'/' + ymd_path if self.date else ''}"
        r = requests.get(sched_url)
        r.raise_for_status()
        self.soup = BS(r.content.decode(), features="html5lib")
        self.broadcasts = [
            Broadcast.from_soup(b)
            for b in self.soup.select(".broadcast")
        ]

    def __repr__(self):
        return f"Schedule for {self.channel.title} on {self.date}"

class Broadcast:
    def __init__(self, dt, pid, title, subtitle):
        self.time = dt
        self.pid = pid
        self.title = title
        self.subtitle = subtitle

    @classmethod
    def from_soup(cls, bsoup):
        """
        Parse a `div.broadcast` HTML tag in BeautifulSoup.
        """
        pid = bsoup.select_one("*[data-pid]")
        title = bsoup.select_one(".programme__titles .programme__title")
        subtitle = bsoup.select_one(".programme__titles .programme__subtitle")
        text_tags = title, subtitle
        dt = bsoup.select_one("h3.broadcast__time[content]")
        if not all([pid, dt, *text_tags]):
            raise ValueError(f"Missing one or more of: {pid=} {title=} {subtitle=}")
        title, subtitle = [x.text for x in text_tags]
        pid = pid.attrs["data-pid"]
        dt = datetime.fromisoformat(dt.attrs["content"])
        return cls(dt, pid, title, subtitle)
