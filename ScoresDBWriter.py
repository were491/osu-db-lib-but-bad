from typing import Iterable

from IncrementalDBWriter import IncrementalDBWriter
from Utils import mods_to_int
from Enums import Mods


class ScoresDBWriter(IncrementalDBWriter):
    def __init__(self, filename: str, overwrite: bool = False):
        super().__init__(filename, overwrite)

    def _write_beatmaps(self, maps: Iterable):
        for m in maps:
            self._write_string(m.beatmap_hash)
            self._write_int(m.num_scores)

            # TODO: add an individual score to be written?
            for score in m.scores:
                self._write_byte(score.mode_played)
                self._write_int(score.replay_version)
                self._write_string(score.beatmap_hash)
                self._write_string(score.player_name)
                self._write_string(score.replay_hash)

                self._write_short(score.num_300s)
                self._write_short(score.num_100s)
                self._write_short(score.num_50s)
                self._write_short(score.num_gekis)
                self._write_short(score.num_katus)
                self._write_short(score.num_misses)

                self._write_int(score.score_earned)
                self._write_short(score.max_attained_combo)
                self._write_bool(score.perfect_combo)
                self._write_int(mods_to_int(score.mods_used))

                # It seems that here it actually writes a 0x00 instead of a 0x0b so yea
                # well, i'm just gonna update the actual function instead ngl
                # turns out changing the function itself breaks osu!.db sometimes but i rely on this to fast cache soo
                # TODO fix maybe someday
                # self._write_string("")
                self._write_byte(0x00)

                self._write_long(score.timestamp)
                self._write_int(4294967295)  # equal to -1
                self._write_long(score.online_score_id)
                if Mods.TARGET_PRACTICE in score.mods_used:
                    self._write_double(score.tp_accuracy_total)

    def _write_metadata(self):
        pass
