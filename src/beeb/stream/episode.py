from .station import Station
from ..share.time import cal_path

__all__ = ["Programme", "Episode"]

class Programme(Station):
    def __init__(self, station, programme):
        super().__init__(station)
        self.programme = programme
    
    @property
    def _store_dir(self):
        return super()._store_dir / self.programme

    programme_dir = _store_dir

    @property
    def programme(self):
        return self._programme

    @programme.setter
    def programme(self, p):
        self._programme = p
    
    @property
    def programme_parts(self):
        return self.broadcaster, self.station, self.programme

    @property
    def __programme__(self):
        return f"programme⠶{self.programme} on {self.__station__}"

    def __repr__(self):
        return self.__programme__


class Episode(Programme):
    def __init__(self, station, programme, date):
        super().__init__(station, programme)
        self.date = date

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, d):
        self._date = d
    
    @property
    def _store_dir(self):
        return super()._store_dir / cal_path(self.date)

    episode_dir = _store_dir

    @property
    def download_dir(self):
        return self.episode_dir / "assets"

    @property
    def __episode__(self):
        return f"episode⠶{self.date} of {self.__programme__}"

    def __repr__(self):
        return self.__episode__
