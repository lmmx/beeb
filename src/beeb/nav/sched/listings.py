from functools import partial
from .async_utils import fetch_schedules
from .remote import RemoteMixIn
from .sched import ChannelSchedule
from .search import ScheduleSearchMixIn
from ..channel_ids import ChannelPicker
from ...time import parse_abs_from_rel_date, parse_date_range
from ...share import batch_multiprocess_with_return

__all__ = ["ChannelListings"]


class ChannelListings(ScheduleSearchMixIn, RemoteMixIn):
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
                parse_abs_from_rel_date(self.from_date, ymd_ago=(0, 0, i)),
                defer_pull=defer_pull,
            )
            for i in range(self.n_days)
        ]

    def fetch_schedules(self, verbose=False):
        fetch_schedules(self.urlset, self.schedules)
        self.boil_all_schedules(verbose=verbose)

    def boil_all_schedules(self, verbose=False):
        recipe_list = [
            partial(s.boil_broadcasts, return_broadcasts=True) for s in self.schedules
        ]
        # Batch the soup parsing on all cores then sort to regain chronological order
        all_scheduled_broadcasts = sorted(
            batch_multiprocess_with_return(
                recipe_list, show_progress=verbose, tqdm_desc="Boiling schedules..."
            ),
            key=lambda b: b[0].time,
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
