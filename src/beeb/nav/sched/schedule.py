from bs4 import BeautifulSoup as BS
from .broadcasts import Broadcast
from .remote import RemoteMixIn
from ..search import ScheduleSearchMixIn
from ..channel_ids import ChannelPicker
from ...share.http_utils import GET
from ...share.time import parse_abs_from_rel_date, cal_path

__all__ = ["ChannelSchedule"]


class ChannelSchedule(ScheduleSearchMixIn, RemoteMixIn):
    """
    ChannelSchedule for the channel specified by ID in the init method or using
    the constructor classmethod `from_channel_name` which retrieves the channel
    ID from a string (the shortname given in `beeb.nav.channel_ids`).

    The contents of a ChannelSchedule is the schedule listings for a single day,
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

    def __init__(self, channel_id, date=None, defer_pull=False):
        self.channel_id = channel_id
        self.date = date
        self.defer_pull = defer_pull
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
        ch = ChannelPicker.by_name(name, must_exist=True)
        return cls(ch.channel_id, date=date)

    @property
    def ymd_path(self):
        return "/".join(cal_path(self.date, as_tuple=True)) if self.date else None

    @property
    def sched_url(self):
        return f"{self.base_url}{'/' + self.ymd_path if self.date else ''}"

    def parse_schedule(self):
        if self.date is None:
            self.date = parse_abs_from_rel_date()
        if not self.defer_pull:
            # deferred for async procedure
            self.pull_and_parse()

    def pull_and_parse(self):
        r = GET(self.sched_url, raise_for_status=True)
        self.boil_broadcasts(r.content.decode())

    def boil_broadcasts(self, soup=None, raw=True, return_broadcasts=False):
        "Populate `.broadcasts` attribute with a list parsed from `soup`"
        if raw:
            # Prepare the soup from raw HTML
            if not soup:
                # Retrieve soup from frozen (async fetch put it there)
                soup = self.frozen_soup
            soup = BS(soup, features="html5lib")
        broadcasts = [Broadcast.from_soup(b) for b in soup.select(".broadcast")]
        # After parsing, filter out the next day's results (deduplicate listings)
        broadcasts = [
            b for b in broadcasts if (b.time.year, b.time.month, b.time.day) == self.ymd
        ]
        if return_broadcasts:
            return broadcasts
        else:
            self.broadcasts = broadcasts

    def __repr__(self):
        return f"ChannelSchedule for {self.channel.title} on {self.date}"
