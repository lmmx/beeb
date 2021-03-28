from ..api.url_helpers import EpisodeStreamPartURL

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
