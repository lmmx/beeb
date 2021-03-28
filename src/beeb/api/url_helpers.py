__all__ = ["EpisodeStreamPartURL"]

class EpisodeStreamPartURL:
    def __init__(self, url_prefix, filename_prefix, filename_sep, url_suffix):
        self.url_prefix = url_prefix
        self.filename_prefix = filename_prefix
        self.filename_sep = filename_sep
        self.url_suffix = url_suffix

    def make_init_url(self, url_suffix=".dash"):
        return StreamInitURL(
            self.url_prefix, self.filename_prefix, self.filename_sep, url_suffix
        )

    def make_part_url(self, int_i):
        return StreamPartURL(
            int_i,
            self.zfill,
            self.url_prefix,
            self.filename_prefix,
            self.filename_sep,
            self.url_suffix,
        )


class StreamInitURL(EpisodeStreamPartURL):
    def __repr__(self):
        return f"{self.url_prefix}{self.filename_prefix}{self.url_suffix}"


class StreamPartURL(EpisodeStreamPartURL):
    def __init__(
        self, int_i, zfill, url_prefix, filename_prefix, filename_sep, url_suffix
    ):
        super().__init__(url_prefix, filename_prefix, filename_sep, url_suffix)
        self.zfill = zfill
        self.int_i = int_i

    @property
    def str_i(self):
        return str(self.int_i).zfill(self.zfill)

    def __repr__(self):
        return (
            f"{self.url_prefix}{self.filename_prefix}{self.filename_sep}"
            f"{self.str_i}{self.url_suffix}"
        )
