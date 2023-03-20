from IncrementalDBWriter import IncrementalDBWriter
from typing import Iterable
from Utils import mods_to_int


class OsuDBWriter(IncrementalDBWriter):
    def __init__(self, filename: str, overwrite: bool = False):
        super().__init__(filename, overwrite)

        self.folder_count: int = NotImplemented
        self.account_unlocked: bool = NotImplemented
        self.date_unlocked: int = NotImplemented
        self.player_name: str = NotImplemented
        self.user_permissions: int = NotImplemented

    def _write_datetime(self, val: int):
        """.NET DateTime"""
        self._write_long(val)

    def _write_int_double_pair(self, val1: int, val2: float):
        self._write_byte(0x08)
        self._write_int(val1)

        self._write_byte(0x0d)
        self._write_double(val2)

    def _write_beatmaps(self, maps: Iterable):
        for m in maps:
            if self.db_version < 20191106:
                # TODO calculator for this
                self._write_int(m.size_of_entry)

            self._write_string(m.song_artist)
            self._write_string(m.song_artist_unicode)
            self._write_string(m.song_title)
            self._write_string(m.song_title_unicode)
            self._write_string(m.creator)
            self._write_string(m.difficulty)
            self._write_string(m.mp3_name)
            self._write_string(m.beatmap_hash)
            self._write_string(m.beatmap_filename)
            
            self._write_byte(m.status)
            self._write_short(m.num_circles)
            self._write_short(m.num_sliders)
            self._write_short(m.num_spinners)
            self._write_long(m.last_modification_time)

            if self.db_version < 20140609:
                self._write_byte(round(m.approach_rate))
                self._write_byte(round(m.circle_size))
                self._write_byte(round(m.hp_drain))
                self._write_byte(round(m.overall_difficulty))
            else:
                self._write_single(m.approach_rate)
                self._write_single(m.circle_size)
                self._write_single(m.hp_drain)
                self._write_single(m.overall_difficulty)

            self._write_double(m.slider_velocity)

            if self.db_version >= 20140609:
                self._write_int(len(m.star_ratings_std))
                for mods, sr in m.star_ratings_std.items():
                    self._write_int_double_pair(mods_to_int(mods), sr)

                self._write_int(len(m.star_ratings_taiko))
                for mods, sr in m.star_ratings_taiko.items():
                    self._write_int_double_pair(mods_to_int(mods), sr)

                self._write_int(len(m.star_ratings_ctb))
                for mods, sr in m.star_ratings_ctb.items():
                    self._write_int_double_pair(mods_to_int(mods), sr)

                self._write_int(len(m.star_ratings_mania))
                for mods, sr in m.star_ratings_mania.items():
                    self._write_int_double_pair(mods_to_int(mods), sr)

            self._write_int(m.drain_time)
            self._write_int(m.total_time)
            self._write_int(m.preview_timestamp)

            self._write_int(len(m.timing_points))
            for pt in m.timing_points:
                self._write_double(pt.bpm)
                self._write_double(pt.offset)
                self._write_bool(not pt.inherited)

            self._write_int(m.difficulty_id)
            self._write_int(m.beatmap_id)
            self._write_int(m.thread_id)
            self._write_byte(m.highest_grade_std)
            self._write_byte(m.highest_grade_taiko)
            self._write_byte(m.highest_grade_ctb)
            self._write_byte(m.highest_grade_mania)
            self._write_short(m.local_offset_ms)
            self._write_single(m.stack_leniency)
            self._write_byte(m.intended_gameplay_mode)
            self._write_string(m.song_source)
            self._write_string(m.song_tags)
            self._write_short(m.online_offset_ms)
            self._write_string(m.font_used_for_song_title)  # Seems to get 0x00'd sometimes (true empty string)
            self._write_bool(m.is_song_unplayed)
            self._write_long(m.last_played)
            self._write_bool(m.is_osz2_format)
            self._write_string(m.map_folder)
            self._write_long(m.last_checked_against_osu_repo)
            self._write_bool(m.user_ignored_beatmap_hitsounds)
            self._write_bool(m.user_ignored_beatmap_skin)
            self._write_bool(m.user_disabled_storyboard)
            self._write_bool(m.user_disabled_video)
            self._write_bool(m.visual_override)

            if self.db_version < 20140609:
                self._write_short(m.unknown_short_value)

            self._write_int(m.last_modification_time_cursed)
            self._write_byte(m.mania_scroll_speed)

    def _write_metadata(self):
        self._write_int(self.folder_count)
        self._write_bool(self.account_unlocked)
        self._write_datetime(self.date_unlocked)
        self._write_string(self.player_name)

    def close(self):
        self._write_int(self.user_permissions)
        super().close()
