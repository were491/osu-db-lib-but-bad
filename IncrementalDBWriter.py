from DBWriter import DBWriter
from abc import ABC, abstractmethod
from typing import Iterable, Sized, Union


class IncrementalDBWriter(DBWriter, ABC):
    def __init__(self, filename: str, overwrite: bool):
        super().__init__(filename, overwrite)

        self.__maps_count_ptr = None
        self.__maps_written = 0
        self.__wrote_metadata = False

    # Abstract methods to do the actual work, the public methods are just a wrapper.
    @abstractmethod
    def _write_beatmaps(self, maps: Iterable):
        pass

    def write_beatmaps(self, maps: Union[Iterable, Sized]):
        if not self.__wrote_metadata:
            raise ValueError("Can't write maps before metadata!")

        self._write_beatmaps(maps)
        self.__maps_written += len(maps)

        # update the num. of maps written
        cur_pos = self._tell()
        self._seek(self.__maps_count_ptr)
        self._write_int(self.__maps_written)
        self._seek(cur_pos)

    @abstractmethod
    def _write_metadata(self):
        pass

    def write_metadata(self):
        if self.__wrote_metadata:
            raise SyntaxError("I don't even know what to put in these error messages anymore!")

        super()._write_db_version()
        self._write_metadata()

        self.__maps_count_ptr = self._tell()
        self._write_int(0)
        self.__wrote_metadata = True
