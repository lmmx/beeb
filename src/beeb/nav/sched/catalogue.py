from .async_utils import fetch_episode_metadata
from .programme import Programme
from .listings import ChannelListings
from ...api.json_helpers import EpisodeMetadataPidJson
from httpx import RemoteProtocolError
from h2.exceptions import ProtocolError
from sys import stderr

__all__ = ["ProgrammeCatalogue"]

class ProgrammeCatalogue(dict):
    def __init__(self, station_name, with_genre=False, n_days=30, async_pull=True):
        """
        Given a channel name, build a dict of programme PIDs and programme titles.
        If `with_genre` is True, make the value a 2-tuple of (title, genre).
        """
        self.genred = with_genre
        listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
        if async_pull:
            self.async_pull_and_parse(listings)
        else:
            self.pull_and_parse(listings)

    def pull_and_parse(self, listings):
        for episode in listings.all_broadcasts:
            if episode.title in self.episode_titles:
                #print(episode.title, episode.pid)
                continue
            try:
                # Obtain programme PID, programme title, and [if genred] programme genre
                if self.genred:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title_genre
                else:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title
                # EpisodeMetadataPidJson methods return same arg order as Programme takes
                programme_info = parse_json(episode.pid)
                # if genred is False, opt_genre will simply be an empty list
                prog_pid, working_title, *opt_genre = programme_info
                if prog_pid in self:
                    continue # Already processed this programme
                programme = Programme(*programme_info)
            except KeyError as e:
                # One off programmes don't have a "parent" key (not a "series"/"brand")
                continue
            finally:
                self.record_programme(programme)

    def async_pull_and_parse(self, listings, pbar=None, verbose=False, n_retries=3):
        # (Due to httpx client bug documented in issue 6 of beeb issue tracker)
        for i in range(n_retries):
            try:
                fetch_episode_metadata(listings, pbar=pbar, verbose=verbose)
            except (ProtocolError, RemoteProtocolError) as e:
                if verbose:
                    print(f"Error occurred {e}, retrying", file=stderr)
                if i == n_retries - 1:
                    raise e # # Persisted after all retries, so throw it, don't proceed
                # Otherwise retry, connection was terminated due to httpx bug (see #6)
            else:
                break # exit the for loop if it succeeds
        self.listings = listings # broadcasts got `.frozen_data` attrib of JSON string
        for b in self.listings.all_broadcasts:
            try:
                if self.genred:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title_genre
                else:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title
                if not hasattr(b, "frozen_data"):
                    # The episode was skipped and no data stored on it, so skip here too
                    continue
                programme_info = parse_json(b.frozen_data.episode_pid, prefab=b.frozen_data)
                prog_pid, working_title, *opt_genre = programme_info
                if prog_pid in self:
                    continue # Already processed this programme
                programme = Programme(*programme_info)
            except KeyError as e:
                # One off programmes don't have a "parent" key (not a "series"/"brand")
                continue
            finally:
                self.record_programme(programme)

    def record_programme(self, programme):
        pd_val = (programme.title, programme.genre) if self.genred else programme.title
        self.setdefault(programme.pid, pd_val)

    @property
    def episode_titles(self):
        return (v[0] for v in self.values()) if self.genred else self.values()

    @property
    def keyed_by_genre(self):
        if not self.genred:
            raise ValueError("Catalogue was not built with genres")
        genre_dict = {}
        for genre_title, programme_pid_and_title in (
            [v[1], (k, v[0])]
            for (k,v) in self.items()
        ):
            genre_dict.setdefault(genre_title, [])
            genre_dict[genre_title].append(programme_pid_and_title)
        return genre_dict
