from BaseReader import BaseReader
from Datatypes import Score
from Utils import *


class ReplayReader(BaseReader):
    # Yes, I know this is redundant.
    def __init__(self, filename: str):
        super().__init__(filename)
        self.replay_size = None  # int
        self.metadata = None  # Score
        self.life_bar_graph = None  # dict[int, float]

        self.replay_frames = None  # list[tuple[int, float, float, int]].
        self.replay_seed = None

    # Returns successfully loaded or not, currently always True
    def __load_life_bar_graph(self) -> bool:
        self.life_bar_graph = dict()

        data = [frame.split('|') for frame in self._read_string().split(',')][:-1]
        for frame in data:
            self.life_bar_graph[int(frame[0])] = float(frame[1])

        return True

    # Returns successfully loaded or not, currently always True
    def __load_replay_data(self, replay_version: int) -> bool:
        self.replay_frames = []

        self.replay_size = self._read_int()
        data = [frame.split('|') for frame in self._read_lzma(self.replay_size).decode("utf-8").split(',')][:-1]

        # TODO make a Keys enum for the keypresses and also like make the entire replay writer class lmao
        # If version >= 20130319, last item is -12345|0|0|seed.
        if replay_version >= 20130319:
            self.replay_seed = int(data.pop()[3])

        for tick in data:
            self.replay_frames.append((
                int(tick[0]),
                float(tick[1]),
                float(tick[2]),
                int(tick[3])
            ))

        return True

    # Returns successfully loaded or not
    def load(self) -> bool:
        try:
            mode_played = GameplayMode(self._read_byte())
            replay_version = self._read_int()
            beatmap_hash = self._read_string()
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

            if not self.__load_life_bar_graph():
                return False

            timestamp = self._read_long()

            if not self.__load_replay_data(replay_version):
                return False

            online_score_id = self._read_long()

            if contains_all_mods(mods_used, [Mods.TARGET_PRACTICE]):
                tp_accuracy_total = self._read_double()
            else:
                tp_accuracy_total = None

            self.metadata = Score(
                        replay_version,
                        replay_hash,
                        beatmap_hash,
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
                    )
            return True

        except EOFError:
            return False
