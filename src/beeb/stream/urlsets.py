from .async_utils import fetch_urlset
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
        return self.size if self.zero_based else self.size + 1

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
        return cls(last_file_num, url_prefix, fname_prefix, fname_sep, url_suffix)

    fetch_urlset = fetch_urlset
