from ..nav import ChannelPicker
from ..data.store import _dir_path as store_dir

__all__ = ["Broadcaster", "Station"]

class Broadcaster:
    "BBC is the only broadcaster supported by beeb"
    def __init__(self):
        self._broadcaster = "bbc"

    @property
    def broadcaster(self):
        return self._broadcaster

    @property
    def __broadcaster__(self):
        return f"broadcaster⠶{self.broadcaster}"

    def __repr__(self):
        return self.__broadcaster__
    
    @property
    def _root_store_dir(self):
        "Overridable by subclass: default download directory root"
        return store_dir
    
    @property
    def _store_dir(self):
        return self._root_store_dir

class Station(Broadcaster):
    def __init__(self, station):
        super().__init__()
        self.station = station

    @property
    def station(self):
        return self._station

    @station.setter
    def station(self, s):
        self._station = s

    @property
    def __station__(self):
        return f"station⠶'{self.station_title}' (id⠶'{self.station_id}')"

    def __repr__(self):
        return self.__station__

    @property
    def channel(self):
        return ChannelPicker.by_name(self.station)

    @property
    def station_id(self):
        return self.channel.channel_id

    @property
    def station_title(self):
        return self.channel.title
    
    @property
    def _store_dir(self):
        return super()._store_dir / self.station
