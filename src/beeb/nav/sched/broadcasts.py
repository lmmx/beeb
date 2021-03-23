from datetime import datetime

__all__ = ["Broadcast"]


class Broadcast:
    def __init__(self, dt, pid, title, subtitle, synopsis):
        self.time = dt
        self.pid = pid
        self.title = title
        self.subtitle = subtitle
        self.synopsis = synopsis

    @classmethod
    def from_soup(cls, bsoup):
        """
        Parse a `div.broadcast` HTML tag in BeautifulSoup.
        """
        pid = bsoup.select_one("*[data-pid]")
        title = bsoup.select_one(".programme__titles .programme__title")
        subtitle = bsoup.select_one(".programme__titles .programme__subtitle")
        synopsis = bsoup.select_one(".programme__body .programme__synopsis span")
        text_tags = title, subtitle, synopsis
        dt = bsoup.select_one("h3.broadcast__time[content]")
        if not all([pid, dt, title]):
            # Allow the others (subtitle and synopsis) to be missing
            raise ValueError(
                f"Missing one or more of: " f"{pid=} {dt=} {title=} {subtitle=}"
            )
        title, subtitle, synopsis = [
            x.text if x else "" for x in text_tags
        ]  # ensure strings even if missing, title is ensured to exist
        pid = pid.attrs["data-pid"]
        dt = datetime.fromisoformat(dt.attrs["content"])
        return cls(dt, pid, title, subtitle, synopsis)

    @property
    def date_repr(self):
        return self.time.strftime("%d/%m/%Y")

    @property
    def time_repr(self):
        return self.time.strftime("%H:%M")

    @property
    def day_of_week(self):
        return self.time.strftime("%a")

    def __repr__(self):
        date_str = f"{self.day_of_week} {self.date_repr}"
        return f"{self.time_repr} on {date_str} — {self.title}"
