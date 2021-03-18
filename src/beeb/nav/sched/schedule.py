import httpx
import re
from bs4 import BeautifulSoup as BS
from ..channel_ids import ChannelPicker
from ...time import parse_abs_from_rel_date, cal_path, parse_date_range
from ...share import batch_multiprocess_with_return
from .async_utils import fetch_schedules
from datetime import datetime
from functools import partial

__all__ = ["ChannelSchedule", "ChannelListings", "Broadcast"]

class RemoteMixIn:
    @property
    def channel(self):
        return ChannelPicker.by_id(self.channel_id)


class ChannelSchedule(RemoteMixIn):
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
        r = httpx.get(self.sched_url)
        r.raise_for_status()
        self.boil_broadcasts(r.content.decode())

    def boil_broadcasts(self, soup=None, raw=True, return_broadcasts=False):
        "Populate `.broadcasts` attribute with a list parsed from `soup`"
        if raw:
            # Prepare the soup from raw HTML
            if not soup:
                # Retrieve soup from frozen (async fetch put it there)
                soup = self.frozen_soup
            soup = BS(soup, features="html5lib")
        broadcasts = [
            Broadcast.from_soup(b) for b in soup.select(".broadcast")
        ]
        # After parsing, filter out the next day's results (deduplicate listings)
        broadcasts = [
            b for b in broadcasts
            if (b.time.year, b.time.month, b.time.day) == self.ymd
        ]
        if return_broadcasts:
            return broadcasts
        else:
            self.broadcasts = broadcasts

    def __repr__(self):
        return f"ChannelSchedule for {self.channel.title} on {self.date}"

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
        if not all([pid, dt, title]):
            # Allow the others (subtitle and synopsis) to be missing
            raise ValueError(
                f"Missing one or more of: "
                f"{pid=} {dt=} {title=} {subtitle=}"
            )
        title, subtitle, synopsis = [
            x.text if x else "" for x in text_tags
        ] # ensure strings even if missing, title is ensured to exist
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

class ChannelListings(RemoteMixIn):
    """
    Listings for a given channel
    """
    def __init__(self, channel_id, from_date=None, to_date=None, n_days=None):
        self.channel_id = channel_id
        from_date, to_date, n_days = parse_date_range(from_date, to_date, n_days)
        self.from_date, self.to_date, self.n_days = from_date, to_date, n_days
        self.schedules = self.make_schedules()
        self.fetch_schedules()

    @property
    def urlset(self):
        "Generator of URLs for async fetching"
        return (s.sched_url for s in self.schedules)

    def make_schedule(self, date, defer_pull=True):
        "Create schedule object; includes channel ID error handling"
        return ChannelSchedule(self.channel_id, date=date, defer_pull=defer_pull)

    def make_schedules(self, defer_pull=True):
        """
        Make and return a list of ChannelSchedule objects and pull their
        URLs collectively in an efficient async procedure (not seriallly).
        """
        return [
            self.make_schedule(
                parse_abs_from_rel_date(self.from_date, ymd_ago=(0,0,i)),
                defer_pull=defer_pull
            )
            for i in range(self.n_days)
        ]


    def fetch_schedules(self, verbose=False):
        fetch_schedules(self.urlset, self.schedules)
        self.boil_all_schedules(verbose=verbose)

    def boil_all_schedules(self, verbose=False):
        recipe_list = [
            partial(s.boil_broadcasts, return_broadcasts=True)
            for s in self.schedules
        ]
        # Batch the soup parsing on all cores then sort to regain chronological order
        all_scheduled_broadcasts = sorted(
            batch_multiprocess_with_return(
                recipe_list, show_progress=verbose, tqdm_desc="Boiling schedules..."
            ),
            key=lambda b: b[0].time
        )
        for s, b in zip(self.schedules, all_scheduled_broadcasts):
            s.broadcasts = b


    @classmethod
    def from_channel_name(cls, name, from_date=None, to_date=None, n_days=None):
        ch = ChannelPicker.by_name(name, must_exist=True)
        return cls(ch.channel_id, from_date=from_date, to_date=to_date, n_days=n_days)

    @property
    def date_repr(self):
        return self.time.strftime("%d/%m/%Y")

    @property
    def time_repr(self):
        return self.time.strftime("%H:%M")

    def __repr__(self):
        return (
            f"ChannelListings for {self.channel.title} "
            f"from {self.from_date} to {self.to_date} ({self.n_days} days)"
        )
