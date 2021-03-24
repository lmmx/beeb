from .programme import Programme
from .listings import ChannelListings
from ...api.json_helpers import EpisodeMetadataPidJson

__all__ = ["ProgrammeCatalogue"]

class ProgrammeCatalogue(dict):
    def __init__(self, station_name, with_genre=False, n_days=30):
        """
        Given a channel name, build a dict of programme PIDs and programme titles.
        If `with_genre` is True, make the value a 2-tuple of (title, genre).
        """
        self.genred = with_genre
        listings = ChannelListings.from_channel_name(station_name, n_days=n_days)
        for episode in listings.all_broadcasts:
            if episode.title in self.episode_titles:
                #print(episode.title, episode.pid)
                continue
            try:
                # Obtain programme PID, programme title, and [if with_genre] programme genre
                if with_genre:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title_genre
                else:
                    parse_json = EpisodeMetadataPidJson.get_programme_pid_title
                # EpisodeMetadataPidJson methods return same arg order as Programme takes
                programme_info = parse_json(episode.pid)
                # if with_genre is False, opt_genre will simply be an empty list
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
        genre_dict = {}
        for genre_title, programme_pid_and_title in (
            [v[1], (k, v[0])]
            for (k,v) in self.items()
        ):
            genre_dict.setdefault(genre_title, [])
            genre_dict[genre_title].append(programme_pid_and_title)
        return genre_dict
