from ..sched.programme import Programme
from ..sched.listings import ChannelListings
from ..search import CatalogueSearchMixIn
from ...api.json_helpers import EpisodeMetadataPidJson
from ...share.db_utils import CatalogueDB
from ...share.http_utils import async_errors
from sys import stderr

__all__ = ["ProgrammeCatalogue"]

class ProgrammeCatalogue(CatalogueSearchMixIn, dict):
    def __init__(self, station_name, with_genre=False, n_days=30, async_pull=True, store=False):
        """
        Given a channel name, build a dict of programme PIDs and programme titles.
        If `with_genre` is True, make the value a 2-tuple of (title, genre).
        """
        self.genred = with_genre
        self.station_name = station_name
        self.n_days = n_days
        # n_days = 0 will be parsed as None-like and default to 30, so skip manually
        if n_days > 0:
            listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
            if async_pull:
                self.async_pull_and_parse(listings)
            else:
                self.pull_and_parse(listings)
            if store:
                self.store_db()

    def pull_and_parse(self, listings):
        self.parse_broadcast_records(listings.all_broadcasts, sync=True)

    def async_pull_and_parse(self, listings, pbar=None, verbose=False, n_retries=3):
        for i in range(n_retries):
            try:
                listings.fetch_episode_metadata(pbar=pbar, verbose=verbose)
            except async_errors as e:
                if verbose:
                    print(f"Error occurred {e}, retrying", file=stderr)
                if i == n_retries - 1:
                    raise e # # Persisted after all retries, so throw it, don't proceed
                # Otherwise retry, connection was terminated due to httpx bug (see #6)
            else:
                break # exit the for loop if it succeeds
        self.parse_broadcast_records(listings.all_broadcasts, sync=False)

    def parse_broadcast_records(self, broadcasts, sync):
        """
        Given a list of all_broadcasts for some listings and a bool `sync` indicating
        whether it follows a synchronous or asynchronous routine, update the dict with
        the programme info in the broadcasts (or 'frozen' in them if async).
        """
        for b in broadcasts:
            if sync:
                if b.title in self.episode_titles:
                    continue
            try:
                if self.genred:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title_genre
                else:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title
                if not sync and not hasattr(b, "frozen_data"):
                    # The episode was skipped and no data stored on it, so skip here too
                    continue
                ep_pid = b.pid if sync else b.frozen_data.episode_pid
                prefab = None if sync else b.frozen_data
                # Obtain program PID from episode PID, also title and possibly genre
                prog_pid, prog_title, *opt_genre = parse_json(ep_pid, prefab=prefab)
                prog_genre = opt_genre[0] if self.genred else None
                if prog_pid in self:
                    continue # Already processed this programme
                prog = Programme(prog_pid, prog_title, prog_genre, self.station_name)
            except KeyError as e:
                # One off programmes don't have a "parent" key (not a "series"/"brand")
                continue
            else:
                self.record_programme(prog)

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

    @classmethod
    def regenerate_from_db(cls, station_name, with_genre=True):
        catalogue = cls(station_name, with_genre=True, n_days=0)
        catalogue.ensure_db(no_touch=True)
        db_entries = catalogue.retrieve_station_in_db()
        genres = [e[2] for e in db_entries] # peek at the genres
        catalogue.genred = any(genres) # Set to False if all genres are `None`
        for pid, title, genre, station in db_entries:
            prog = Programme(pid, title, genre, station)
            catalogue.record_programme(prog)
        if not with_genre:
            catalogue.ungenre() # Ensure removed post-hoc if not desired
        return catalogue
    
    @classmethod
    def lazy_generate(
            cls, station_name, genred=True, n_days=30, async_pull=True, store=True
        ):
        """
        Try to reload from database, only pull fresh catalogue if not available.
        """
        # Set up a temporary object that'll be overwritten after ensuring exists
        catalogue = cls(station_name, with_genre=genred, n_days=0)
        try:
            catalogue.ensure_db(no_touch=True)
        except FileNotFoundError:
            db_exists = False
        else:
            db_exists = catalogue.db.exists()
        if db_exists and catalogue.db.has_station(station_name):
            catalogue = cls.regenerate_from_db(station_name)
            if genred and not catalogue.genred:
                print(f"(!) The reloaded catalogue is ungenred: {catalogue}")
        else:
            catalogue = cls(
                station_name, with_genre=genred, n_days=n_days, async_pull=async_pull
            )
            if store:
                catalogue.store_db()
        return catalogue

    def ensure_db(self, no_touch=False):
        """
        Run the 'CREATE TABLE IF NOT EXISTS' routine and set `ProgrammeCatalogue.db`,
        but if `no_touch` is True, then raise a `FileNotFoundError` if the database
        doesn't already exist (do not implicitly create it!)
        """
        if not hasattr(self, "db"):
            # creates a sqlite3 database in beeb.data.store
            self.db = CatalogueDB(create=not no_touch, no_touch=no_touch)

    def store_db(self):
        self.ensure_db()
        for pid, value in self.items():
            if self.genred:
                title, genre = value
            else:
                title = value
                genre = None
            self.insert_db_entry(pid, title, genre)

    def insert_db_entry(self, pid, title, genre):
        if self.genred and genre is None:
            raise ValueError("No genre specified but catalogue was built with genres")
        if not hasattr(self, "db"):
            msg = "Create DB before inserting. Hint: `ProgrammeCatalogue.store_db()`"
            raise ValueError(msg)
        self.db.insert_entry(pid, title, genre, station=self.station_name)

    def retrieve_station_in_db(self):
        result = self.db.retrieve_station(self.station_name)
        return result
    
    def retrieve_programme_pid(self, pid):
        result = self.db.retrieve_pid(pid)
        if result:
            return Programme(*result)
        else:
            raise KeyError(f"{pid=} not found in {self.db}")

    def ungenre(self):
        if self.genred:
            for k, v in self.items():
                self.update({k: v[0]})
            self.genred = False
