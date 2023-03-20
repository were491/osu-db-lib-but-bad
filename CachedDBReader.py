from DBReader import DBReader
from abc import ABC, abstractmethod


class CachedDBReader(DBReader, ABC):
    def __init__(self, filename: str):
        super().__init__(filename)

        self.num_beatmaps = NotImplemented
        self._beatmap_pointers_cache = dict()  # <map md5> : <pointer to map>
        self._first_beatmap_pointer = NotImplemented
        self._current_beatmap_pointer = NotImplemented  # used for read_beatmaps_seq

    # Returns status code and list of all beatmaps (if False: that it could read)
    # Read beatmaps from start_pos, returning updated pointer.
    @abstractmethod
    def read_beatmaps(self, num_maps: int, start_pos: int) -> (bool, list, int):
        """Read beatmaps from start_pos, returning updated pointer and the beatmaps."""
        pass

    # Used for caching beatmaps
    def _skip_strings(self, num_strings: int):
        """Skips osu!-style strings. Makes caching maps faster?"""
        for i in range(num_strings):
            if self._read_byte() == 0x00:
                continue

            self._seek(self._read_uleb128(), 1)

    # Slow path by default, intended to be overridden.
    def cache_all_beatmaps(self) -> bool:
        return self.read_all_beatmaps()[0]

    def read_beatmaps_seq(self, num_maps: int) -> (bool, list):
        status, maps, new_ptr = self.read_beatmaps(num_maps, self._current_beatmap_pointer)
        self._current_beatmap_pointer = new_ptr
        return status, maps

    def read_all_beatmaps(self) -> (bool, list):
        """Reads and caches all beatmaps."""
        return self.read_beatmaps(self.num_beatmaps, self._first_beatmap_pointer)[:2]

    # -1 if not found.
    def get_beatmap_in_cache(self, map_hash: str) -> int:
        try:
            return self._beatmap_pointers_cache[map_hash]
        except KeyError:
            return -1
