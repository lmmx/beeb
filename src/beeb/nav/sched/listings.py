from functools import partial
from .async_utils import fetch_schedules, fetch_episode_metadata
from .remote import RemoteMixIn
from .schedule import ChannelSchedule
from ..search import ScheduleSearchMixIn
from ..channel_ids import ChannelPicker
from ...api.json_helpers import EpisodeMetadataPidJson
from ...share import batch_multiprocess_with_return, async_errors
from ...share.time import parse_abs_from_rel_date, parse_date_range

__all__ = ["ChannelListings"]


class ChannelListings(ScheduleSearchMixIn, RemoteMixIn):
    """
    Listings for a given channel
    """
    episode_reader_func = EpisodeMetadataPidJson.reader_func
    fetch_episode_metadata = fetch_episode_metadata # bind as method

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

    def fetch_schedules(self, verbose=False, n_retries=3):
        # (Due to httpx client bug documented in issue 6 of beeb issue tracker)
        for i in range(n_retries):
            try:
                fetch_schedules(self.urlset, self.schedules)
            except async_errors as e:
                if verbose:
                    print(f"Error occurred {e}, retrying")
                if i == n_retries - 1:
                    raise e # # Persisted after all retries, so throw it, don't proceed
                # Otherwise retry, connection was terminated due to httpx bug (see #6)
            else:
                break # exit the for loop if it succeeds
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

    @property
    def all_broadcasts(self):
        "Presuming the schedules are already boiled (i.e. parsed), enumerate broadcasts"
        return [b for s in self.schedules for b in s.broadcasts]

    @property
    def broadcasts_urlset(self):
        "Make a generator to produce the URLs for the broadcasts from all_broadcasts"
        return (
            EpisodeMetadataPidJson(episode.pid, defer_pull=True).url
            for episode in self.all_broadcasts
        )
