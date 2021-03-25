class Programme:
    def __init__(self, pid, title, genre, station):
        self.pid = pid
        self.title = title
        self.genre = genre
        self.station = station

    def __repr__(self):
        # TODO: look up full station title
        prog = f"Programme '{self.title}' (pid: {self.pid}, genre: '{self.genre}')"
        return f"{prog} on {self.station}"
