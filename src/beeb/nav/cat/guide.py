from .catalogue import ProgrammeCatalogue
from ..search import CatalogueSearchMixIn
from ..channel_ids import ChannelPicker

__all__ = ["ProgrammeGuide"]


class ProgrammeGuide(CatalogueSearchMixIn, dict):
    def __init__(
        self, station_names, with_genre=False, n_days=30, async_pull=True, store=False
    ):
        self.genred = with_genre
        self.n_days = n_days
        for n in sorted(station_names):
            self.record_catalogue(n, async_pull=async_pull, store=store)

    def record_catalogue(self, station_name, async_pull=True, store=False):
        if station_name in self:
            raise KeyError(f"{station_name=} is already a recorded key")
        pc = ProgrammeCatalogue(
            station_name=station_name,
            with_genre=self.genred,
            n_days=self.n_days,
            async_pull=async_pull,
            store=store,
        )
        self.update({station_name: pc})

    @classmethod
    def generate_by_names(
        cls,
        station_names,
        lazy=True,
        genred=True,
        n_days=30,
        async_pull=True,
        store=True,
    ):
        """
        Generate programme catalogues for a list of names, e.g.
        `["r1", "r2"]` (matching those in `beeb.nav.channel_ids`)
        """
        guide = cls(station_names=[], n_days=0)
        for station_name in station_names:
            if station_name in guide:
                raise KeyError(f"{station_name=} is already a recorded key")
            pc = (
                ProgrammeCatalogue.lazy_generate(
                    station_name,
                    genred=genred,
                    n_days=n_days,
                    async_pull=async_pull,
                    store=store,
                )
                if lazy
                else ProgrammeCatalogue(
                    station_name,
                    with_genre=genred,
                    n_days=n_days,
                    async_pull=async_pull,
                    store=store,
                )
            )
            guide.update({station_name: pc})
        return guide

    @classmethod
    def generate_by_category(
        cls, category, lazy=True, genred=True, n_days=30, async_pull=True, store=True
    ):
        """
        Generate programme catalogues for a category of channels, e.g. 'national'
        """
        station_names = ChannelPicker.keys_by_category(category, remove_variants=True)
        guide = cls.generate_by_names(
            station_names, lazy, genred, n_days, async_pull, store
        )
        # May need to retry in case httpx throws ConnectTimeout error?
        return guide

    @classmethod
    def generate_by_titles(
        cls, titles, lazy=True, genred=True, n_days=30, async_pull=True, store=True
    ):
        """
        Generate programme catalogues for a list of titles, e.g.
        `["BBC Radio 1", "BBC Radio 2"]` (matching those in `beeb.nav.channel_ids`)
        """
        if isinstance(titles, str):
            titles = [titles]
        station_names = [ChannelPicker.by_title(t, return_value=False) for t in titles]
        guide = cls.generate_by_names(
            station_names, lazy, genred, n_days, async_pull, store
        )
        return guide
