from .async_utils import fetch_urlset
from ..api import final_m4s_link_from_programme_pid, get_programme_pid_by_name
from ..api.url_helpers import EpisodeStreamPartURL
from pathlib import Path

__all__ = ["StreamUrlSet"]

class StreamUrlSet(EpisodeStreamPartURL):
    def __init__(
        self,
        size,
        url_prefix,
        filename_prefix,
        filename_sep,
        url_suffix,
        zero_based=False,
        zfill=True,
    ):
        super().__init__(url_prefix, filename_prefix, filename_sep, url_suffix)
        self.size = size  # class is an iterator not a list so record size
        self.zfill = len(str(size)) if zfill else 0
        self.zero_based = zero_based
        self.reset_pos()
        self.is_initialised = False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, n):
        self._size = n

    @property
    def pos_end(self):
        "There is already a +1 offset due to inclusion of the DASH URL"
        return self.size -1 if self.zero_based else self.size

    def reset_pos(self):
        self.pos = 0 if self.zero_based else 1

    def increment_pos(self):
        self.pos += 1

    def __repr__(self):
        return f"{self.size} URLs"

    def __iter__(self):
        return next(self)

    def __next__(self):
        while not self.is_initialised:
            self.is_initialised = True
            yield self.make_init_url()
        while self.pos < self.pos_end:
            p = self.pos
            self.increment_pos()
            yield self.make_part_url(p)

    @classmethod
    def from_last_m4s_url(cls, last_url):
        last_filename = Path(Path(last_url).name)
        url_prefix = last_url[: -len(last_filename.name)]
        url_suffix = last_filename.suffix
        fname_prefix, fname_sep, last_file_num = last_filename.stem.rpartition("-")
        if not last_file_num.isnumeric():
            raise ValueError(f"{last_file_num} was non-numeric")
        if fname_prefix == fname_sep == "":
            # rpartition gives two empty strings and the original if separator not found
            raise ValueError("Failed to parse filename (did not contain '-' separator)")
        last_file_num = int(last_file_num)
        n_urls = last_file_num + 1
        return cls(n_urls, url_prefix, fname_prefix, fname_sep, url_suffix)

    @classmethod
    def from_programme_pid(cls, programme_pid, ymd):
        last_link_url = final_m4s_link_from_programme_pid(programme_pid, ymd=ymd)
        return cls.from_last_m4s_url(last_link_url)

    @classmethod
    def from_programme_name(cls, programme_name, station_name, date):
        programme_pid = get_programme_pid_by_name(programme_name, station_name)
        return cls.from_programme_pid(programme_pid, date)

    fetch_urlset = fetch_urlset
