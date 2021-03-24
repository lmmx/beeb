class Programme:
    def __init__(self, pid, title, genre=None):
        self.pid = pid
        self.title = title
        self.genre = genre

    def __repr__(self):
        return f"Programme '{self.title}' (pid: {self.pid}, genre: '{self.genre}')"
