from .episode import Episode
from .preproc import gather_pulled_downloads, mp4_to_wav
from .urlsets import StreamUrlSet
from ..api import get_programme_pid_by_name
from ..share.time import parse_abs_from_rel_date
from pathlib import Path
from tqdm import tqdm

__all__ = ["Stream"]


class Stream(Episode):
    """
    Class representing the MPEG-DASH stream for an episode (i.e. the
    instance of a programme on a specific date) on a BBC radio station.

    When initialised, if `defer_pull` is False (default), the methods
    `pull` (fetch stream parts asynchronously: this should be fast)
    then `preprocess` (gather parts into a single MP4, then transcode
    the WAV to MP4 if `transcode_to_wav` is True) are called.

    The download directory can be changed by overriding the `_root_store_dir`
    property of the `Broadcaster` base class which `Stream` is a subclass of.
    By default, the download directory root is at the package-internal
    path of the `beeb.data.store` module, beneath which are directories
    for station > programme (by PID) > year > month > day.
    """

    def __init__(
        self,
        station,
        programme,
        date,
        urlset,
        defer_pull=False,
        transcode_to_wav=True,
        clean_up=True,
        gathered_filename_stem="episode",
        custom_storage_path=None,
    ):
        # Set repr and directory properties for:
        # station, programme, episode, date
        super().__init__(station, programme, date)
        self.stream_urls = urlset
        self.transcode_to_wav = transcode_to_wav
        self.gathered_filename_stem = gathered_filename_stem
        self.clean_up = clean_up
        if custom_storage_path:
            self.customise_root_store_dir(custom_storage_path)
        if not defer_pull:
            self.pull()
            self.preprocess()

    def pull(self, verbose=False):
        if not self.preprocessed_output_file.exists():
            if verbose:
                print(f"Pulling {self.stream_urls}")
            pbar = tqdm(total=self.stream_urls.size)
            self.stream_urls.fetch_urlset(
                download_dir=self.download_dir, pbar=pbar, verbose=verbose
            )
            pbar.close()
            if verbose:
                print("Done")

    def gathered_filename(self, pre_transcode=False):
        gathered_ext = "wav" if self.transcode_to_wav and not pre_transcode else "mp4"
        return f"{self.gathered_filename_stem}.{gathered_ext}"

    @property
    def preprocessed_output_file(self):
        return self.episode_dir / self.gathered_filename()

    def gather(self):
        gather_pulled_downloads(
            self.download_dir, self.episode_dir, self.gathered_filename_stem
        )

    def preprocess(self):
        """
        Gather stream files into a single MP4 file, and convert to WAV if
        `self.transcode_to_wav` is True. Clean up by deleting the intermediate
        MPEG-DASH files from the assets directory if `self.clean_up` is True.
        """
        if not self.preprocessed_output_file.exists():
            self.gather()
            if self.transcode_to_wav:
                mp4 = self.episode_dir / self.gathered_filename(pre_transcode=True)
                transcoded_wav = mp4_to_wav(mp4)
                if self.clean_up:
                    mp4.unlink(missing_ok=True)
        if self.clean_up and self.download_dir.exists():
            # Cannot actually delete files by name without recreating URLs generator
            file_count_ok = len([*self.download_dir.iterdir()]) == self.stream_urls.size
            no_subdirs = not any(x.is_dir() for x in self.download_dir.iterdir())
            if file_count_ok and no_subdirs:
                for f in self.download_dir.iterdir():
                    f.unlink()
                self.download_dir.rmdir()  # Delete assets directory if empty

    @property
    def stream_urls(self):
        return self._stream_urls

    @stream_urls.setter
    def stream_urls(self, u):
        self._stream_urls = u

    @property
    def stream_len(self):
        return self.stream_urls.size

    @property
    def __stream__(self):
        return f"stream⠶{self.stream_urls} from {self.__episode__}"

    def __repr__(self):
        return self.__stream__

    @classmethod
    def from_name(
        cls,
        station,
        programme_name,
        ymd=None,
        ymd_ago=None,
        defer_pull=False,
        transcode_to_wav=True,
        clean_up=True,
        gathered_filename_stem="episode",
        custom_storage_path=None,
    ):
        programme_pid = get_programme_pid_by_name(programme_name, station)
        date = parse_abs_from_rel_date(ymd=ymd, ymd_ago=ymd_ago)
        ymd = (date.year, date.month, date.day)
        urlset = StreamUrlSet.from_programme_pid(programme_pid, ymd)
        stream = cls(
            station,
            programme_pid,
            date,
            urlset,
            defer_pull=defer_pull,
            transcode_to_wav=transcode_to_wav,
            clean_up=clean_up,
            gathered_filename_stem=gathered_filename_stem,
            custom_storage_path=custom_storage_path,
        )
        return stream
