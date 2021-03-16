import requests
from bs4 import BeautifulSoup as BS
from ..channel_ids import ChannelPicker
from ...time import parse_abs_from_rel_date, cal_path

__all__ = ["Schedule"]

class Schedule:
    """
    Schedule for the channel specified by ID in the init method or using
    the constructor classmethod `from_channel_name` which retrieves the channel
    ID from a string (the shortname given in `beeb.nav.channel_ids`).

    The contents of a Schedule is the schedule listings for a single day,
    and the date can be specified as a datetime object `date`.
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
        self.url = f"{self.common_url_prefix}{self.channel_id}"
        self.parse_schedule()

    @classmethod
    def from_channel_name(cls, name, date=None):
        channel = ChannelPicker.by_name(name, must_exist=True)
        return cls(channel.channel_id, date=date)

    def parse_schedule(self):
        if self.date is None:
            self.date = parse_abs_from_rel_date()
        ymd_path = "/".join(cal_path(self.date, as_tuple=True)) if self.date else None
        sched_url = f"{self.url}{'/' + ymd_path if self.date else ''}"
        r = requests.get(self.url)
        r.raise_for_status()
        self.soup = BS(r.content.decode(), features="html5lib")

    def __repr__(self):
        return f"Schedule for {self.channel.title} on {self.date}"
