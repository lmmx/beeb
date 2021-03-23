from .series import Series
from .listings import ChannelListings
from ...api.json_helpers import EpisodeMetadataPidJson

__all__ = ["SeriesCatalogue"]

class SeriesCatalogue(dict):
    def __init__(self, station_name, with_genre=False, n_days=30):
        """
        Given the name of a channel, build a dict of series PIDs and series titles.
        If `with_genre` is True, make the value a 2-tuple of (title, genre).
        """
        self.genred = with_genre
        listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
        for episode in listings.all_broadcasts:
            if episode.title in self.episode_titles:
                continue # Presume episode titles are unique to a series (wrong!!!)
            try:
                if with_genre:
                    parse_json = EpisodeMetadataPidJson.get_series_pid_title_genre
                else:
                    parse_json = EpisodeMetadataPidJson.get_series_pid_title
                # EpisodeMetadataPidJson methods return same arg order as Series takes
                series = Series(*parse_json(episode.pid))
            except KeyError as e:
                # One off programmes don't have a "parent" key (not a "series"/"brand")
                continue
            finally:
                self.record_series(series)

    def record_series(self, series):
        sd_val = (series.title, series.genre) if self.genred else series.title
        self.setdefault(series.pid, sd_val)

    @property
    def episode_titles(self):
        return (v[0] for v in self.values()) if self.genred else self.values()

    @property
    def keyed_by_genre(self):
        genre_dict = {}
        for genre_title, series_pid_and_title in (
            [v[1], (k, v[0])]
            for (k,v) in self.items()
        ):
            genre_dict.setdefault(genre_title, [])
            genre_dict[genre_title].append(series_pid_and_title)
        return genre_dict
