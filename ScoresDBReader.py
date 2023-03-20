from CachedDBReader import CachedDBReader
from Datatypes import ScoreBeatmap, Score
from Utils import *


# I'd add a function to search within a beatmap's scores by hash, but honestly no one really
# has like a million saved replays on the same map anyway therefore idgaf.
class ScoresDBReader(CachedDBReader):
    def __init__(self, filename: str):
        super().__init__(filename)

        self.num_beatmaps = self._read_int()
        self._first_beatmap_pointer = self._tell()
        self._current_beatmap_pointer = self._tell()

    def read_beatmaps(self, num_maps: int, start_pos: int) -> (bool, list, int):
        self._seek(start_pos)
        beatmaps = []
        try:
            for i in range(num_maps):
                pointer_beginning_of_map = self._tell()
                beatmap_hash = self._read_string()

                num_scores = self._read_int()
                scores = []
                for j in range(num_scores):
                    mode_played = GameplayMode(self._read_byte())
                    replay_version = self._read_int()
                    score_beatmap_hash = self._read_string()  # Different from the name in the dataclass.
                    player_name = self._read_string()
                    replay_hash = self._read_string()
                    num_300s = self._read_short()
                    num_100s = self._read_short()
                    num_50s = self._read_short()
                    num_gekis = self._read_short()
                    num_katus = self._read_short()
                    num_misses = self._read_short()
                    score_earned = self._read_int()
                    max_attained_combo = self._read_short()
                    perfect_combo = self._read_bool()
                    mods_used = int_to_mods(self._read_int())
                    self._read_string()  # Always empty
                    timestamp = self._read_long()
                    self._read_int()  # Always empty
                    online_score_id = self._read_long()

                    if contains_all_mods(mods_used, [Mods.TARGET_PRACTICE]):
                        tp_accuracy_total = self._read_double()
                    else:
                        tp_accuracy_total = None

                    scores.append(Score(
                        replay_version,
                        replay_hash,
                        score_beatmap_hash,
                        player_name,
                        timestamp,
                        online_score_id,
                        mode_played,
                        mods_used,
                        score_earned,
                        max_attained_combo,
                        perfect_combo,
                        num_300s,
                        num_100s,
                        num_50s,
                        num_misses,
                        num_gekis,
                        num_katus,
                        tp_accuracy_total
                    ))

                beatmaps.append(ScoreBeatmap(
                    beatmap_hash,
                    num_scores,
                    scores
                ))

                # Add to cache
                if beatmap_hash not in self._beatmap_pointers_cache.keys():
                    self._beatmap_pointers_cache[beatmap_hash] = pointer_beginning_of_map
            return True, beatmaps, self._tell()
        except EOFError:
            # Database ended early, return what we have.
            return False, beatmaps, self._tell()

    # From 1.089150800000425s to 0.49720130000059726s
    def cache_all_beatmaps(self) -> bool:
        """Caches all beatmap pointers, returns whether successful."""
        self._seek(self._first_beatmap_pointer)
        try:
            for i in range(self.num_beatmaps):
                pointer_beginning_of_map = self._tell()
                beatmap_hash = self._read_string()

                num_scores = self._read_int()
                for j in range(num_scores):
                    # Skip metadata again
                    self._seek(5, 1)
                    self._skip_strings(3)

                    # Skip replay info
                    self._seek(19, 1)
                    mods_used = int_to_mods(self._read_int())

                    # Rest of metadata
                    self._seek(21, 1)

                    if contains_all_mods(mods_used, [Mods.TARGET_PRACTICE]):
                        self._seek(8, 1)

                # Add to cache
                if beatmap_hash not in self._beatmap_pointers_cache.keys():
                    self._beatmap_pointers_cache[beatmap_hash] = pointer_beginning_of_map
            return True
        except EOFError:
            # Database ended early, return False.
            return False
