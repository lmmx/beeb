import sqlite3
from ..data.store import _dir_path as store_path

__all__ = ["CatalogueDB"]


class CatalogueDB:
    filename = "programme_catalogue.db"  # Default value
    directory = store_path

    def __init__(self, dir=directory, filename=filename, create=True, no_touch=False):
        self.directory = dir
        self.filename = filename
        if create:
            self.create(no_touch=no_touch)

    @property
    def path(self):
        return self.directory / self.filename

    def exists(self):
        return self.path.exists()

    def create(self, no_touch=False):
        if no_touch and not self.path.exists():
            raise FileNotFoundError(f"No CatalogueDB at {self.db.path}")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS programmes
                (pid varchar(20), title tinytext, genre tinytext, station varchar(10),
                Constraint pk_pid Primary key(pid, station))
                """
            )

    def connect(self):
        return sqlite3.connect(self.path)

    def insert_entry(self, pid, title, genre, station):
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO programmes VALUES (?,?,?,?)", (pid, title, genre, station)
                )
                conn.commit()
        except Exception as e:
            print(f"{pid=} {title=} {genre=} {station=}")
            raise e

    def retrieve_pid(self, pid):
        with self.connect() as conn:
            query_sql = """
            SELECT * FROM programmes
            WHERE pid == ?
            """
            c = conn.cursor()
            c.execute(query_sql, (pid,))
            return c.fetchone()

    def retrieve_station(self, station_name, fetch_all=True):
        with self.connect() as conn:
            query_sql = """
            SELECT * FROM programmes
            WHERE station == ?
            """
            c = conn.cursor()
            c.execute(query_sql, (station_name,))
            return c.fetchall() if fetch_all else c.fetchone()

    def has_station(self, station_name):
        peek = self.retrieve_station(station_name, fetch_all=False)
        has_station = peek is not None
        return has_station

    def __repr__(self):
        return f"CatalogueDB '{self.filename}' at {self.directory}"
