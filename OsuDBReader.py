from CachedDBReader import CachedDBReader
from Datatypes import BeatmapMetadata, TimingPoint
from Enums import GameplayMode
from Utils import int_to_mods


class OsuDBReader(CachedDBReader):
    def __init__(self, filename: str):
        """Reads osu!.db files."""
        super().__init__(filename)

        self.folder_count = self._read_int()
        self.account_unlocked = self._read_bool()
        self.date_unlocked = self._read_datetime()  # 216000000000 if not banned
        self.player_name = self._read_string()
        self.num_beatmaps = self._read_int()

        self._first_beatmap_pointer = self._tell()
        self._current_beatmap_pointer = self._tell()

        # Jump to end of file to read the user permissions.
        self._seek(-4, 2)
        self.user_permissions = self._read_int()
        self._seek(self._current_beatmap_pointer)

    # DateTime is in Windows ticks anyways...
    def _read_datetime(self) -> int:
        """.NET DateTime"""
        return self._read_long()

    def _read_int_double_pair(self) -> (int, float):
        # Discard the extraneous bytes
        self._read_byte()
        integer_value = self._read_int()

        self._read_byte()
        double_value = self._read_double()

        return integer_value, double_value

    def read_beatmaps(self, num_maps: int, start_pos: int) -> (bool, list, int):
        self._seek(start_pos)
        beatmaps = []
        try:
            for i in range(num_maps):
                pointer_beginning_of_map = self._tell()

                if self.db_version < 20191106:
                    size_of_entry = self._read_int()
                else:
                    size_of_entry = None

                song_artist = self._read_string()
                song_artist_unicode = self._read_string()
                song_title = self._read_string()
                song_title_unicode = self._read_string()
                creator = self._read_string()
                difficulty = self._read_string()
                mp3_name = self._read_string()
                beatmap_hash = self._read_string()
                beatmap_filename = self._read_string()
                status = self._read_byte()
                num_circles = self._read_short()
                num_sliders = self._read_short()
                num_spinners = self._read_short()
                last_modification_time = self._read_long()

                if self.db_version < 20140609:
                    approach_rate = self._read_byte()
                    circle_size = self._read_byte()
                    hp_drain = self._read_byte()
                    overall_difficulty = self._read_byte()
                else:
                    approach_rate = self._read_single()
                    circle_size = self._read_single()
                    hp_drain = self._read_single()
                    overall_difficulty = self._read_single()

                slider_velocity = self._read_double()

                # Cached SRs only existed with version >= 20140609
                star_ratings_std = dict()
                star_ratings_taiko = dict()
                star_ratings_ctb = dict()
                star_ratings_mania = dict()
                if self.db_version >= 20140609:
                    star_ratings_std_count = self._read_int()
                    for j in range(star_ratings_std_count):
                        mods, star_rating = self._read_int_double_pair()
                        star_ratings_std[frozenset(int_to_mods(mods))] = star_rating

                    star_ratings_taiko_count = self._read_int()
                    for j in range(star_ratings_taiko_count):
                        mods, star_rating = self._read_int_double_pair()
                        star_ratings_taiko[frozenset(int_to_mods(mods))] = star_rating

                    star_ratings_ctb_count = self._read_int()
                    for j in range(star_ratings_ctb_count):
                        mods, star_rating = self._read_int_double_pair()
                        star_ratings_ctb[frozenset(int_to_mods(mods))] = star_rating

                    star_ratings_mania_count = self._read_int()
                    for j in range(star_ratings_mania_count):
                        mods, star_rating = self._read_int_double_pair()
                        star_ratings_mania[frozenset(int_to_mods(mods))] = star_rating

                drain_time = self._read_int()
                total_time = self._read_int()
                preview_timestamp = self._read_int()

                timing_points_list = []
                timing_points_count = self._read_int()
                for j in range(timing_points_count):
                    bpm = self._read_double()
                    offset = self._read_double()
                    not_inherited = self._read_bool()
                    timing_points_list.append(TimingPoint(bpm, offset, not not_inherited))
                timing_points = tuple(timing_points_list)

                difficulty_id = self._read_int()
                beatmap_id = self._read_int()
                thread_id = self._read_int()  # 0 if submitted after moddingv2
                # Seems like 9 = no grade achieved.
                highest_grade_std = self._read_byte()
                highest_grade_taiko = self._read_byte()
                highest_grade_ctb = self._read_byte()
                highest_grade_mania = self._read_byte()
                local_offset_ms = self._read_short()
                stack_leniency = self._read_single()  # always a decimal e.g. SL 0.7 -> SL 7 in editor.
                intended_gameplay_mode = GameplayMode(self._read_byte())
                song_source = self._read_string()
                song_tags = self._read_string()
                online_offset_ms = self._read_short()
                font_used_for_song_title = self._read_string()  # e.g. [bold:0,size:20]$44,000\n#pumpmycrunkbeetz
                is_song_unplayed = self._read_bool()
                last_played = self._read_long()
                is_osz2_format = self._read_bool()  # 2012 controversies be like
                map_folder = self._read_string()
                last_checked_against_osu_repo = self._read_long()
                # Local options only. e.g. if they disable video globally
                # then this may be false, but the video still won't play
                user_ignored_beatmap_hitsounds = self._read_bool()
                user_ignored_beatmap_skin = self._read_bool()
                user_disabled_storyboard = self._read_bool()
                user_disabled_video = self._read_bool()
                visual_override = self._read_bool()
                if self.db_version < 20140609:
                    unknown_short_value = self._read_short()
                else:
                    unknown_short_value = None
                last_modification_time_cursed = self._read_int()
                mania_scroll_speed = self._read_byte()

                beatmaps.append(BeatmapMetadata(
                    size_of_entry,
                    last_modification_time,
                    is_osz2_format,
                    map_folder,
                    song_artist,
                    song_artist_unicode,
                    song_title,
                    song_title_unicode,
                    song_source,
                    song_tags,
                    font_used_for_song_title,
                    mp3_name,
                    creator,
                    difficulty,
                    difficulty_id,
                    beatmap_hash,
                    beatmap_filename,
                    status,
                    beatmap_id,
                    thread_id,
                    drain_time,
                    total_time,
                    preview_timestamp,
                    intended_gameplay_mode,
                    online_offset_ms,
                    num_circles,
                    num_sliders,
                    num_spinners,
                    approach_rate,
                    circle_size,
                    hp_drain,
                    overall_difficulty,
                    slider_velocity,
                    stack_leniency,
                    mania_scroll_speed,
                    star_ratings_std,
                    star_ratings_taiko,
                    star_ratings_ctb,
                    star_ratings_mania,
                    timing_points,
                    highest_grade_std,
                    highest_grade_taiko,
                    highest_grade_ctb,
                    highest_grade_mania,
                    local_offset_ms,
                    is_song_unplayed,
                    last_played,
                    last_checked_against_osu_repo,
                    user_ignored_beatmap_hitsounds,
                    user_ignored_beatmap_skin,
                    user_disabled_storyboard,
                    user_disabled_video,
                    visual_override,
                    unknown_short_value,
                    last_modification_time_cursed
                ))

                # Add to cache
                if beatmap_hash not in self._beatmap_pointers_cache.keys():
                    self._beatmap_pointers_cache[beatmap_hash] = pointer_beginning_of_map
            return True, beatmaps, self._tell()
        except EOFError:
            # Database ended early, return what we have.
            return False, beatmaps, self._tell()

    # From 64.07527690000097s to 7.883499000001393s
    def cache_all_beatmaps(self) -> bool:
        # we have to read the maps that are already for sure cached according to _current_beatmap_pointer
        # because it's possible other maps got added to the cache e.g., through a stored pointer.
        self._seek(self._first_beatmap_pointer)
        try:
            for i in range(self.num_beatmaps):
                pointer_beginning_of_map = self._tell()

                if self.db_version < 20191106:
                    entry_size = self._read_int()
                else:
                    entry_size = -1

                # Skip most of the metadata
                self._skip_strings(7)

                beatmap_hash = self._read_string()

                # Skip rest of DB for old versions
                if entry_size != -1:
                    self._seek(pointer_beginning_of_map + entry_size + 1)
                else:
                    self._skip_strings(1)
                    # num circles, sliders, etc.
                    self._seek(15, 1)

                    # Skip diff settings incl. SV
                    if self.db_version < 20140609:
                        self._seek(12, 1)
                    else:
                        self._seek(24, 1)

                    # Skipping star ratings
                    if self.db_version >= 20140609:
                        self._seek(self._read_int() * 14, 1)
                        self._seek(self._read_int() * 14, 1)
                        self._seek(self._read_int() * 14, 1)
                        self._seek(self._read_int() * 14, 1)

                    # Drain time, preview time, etc
                    self._seek(12, 1)

                    # Timing points
                    self._seek(self._read_int() * 17, 1)

                    # Online metadata
                    self._seek(23, 1)
                    self._skip_strings(2)

                    # Online offset
                    self._seek(2, 1)

                    self._skip_strings(1)
                    self._seek(10, 1)

                    self._skip_strings(1)
                    self._seek(13, 1)

                    # Cursed stuff
                    if self.db_version < 20140609:
                        self._seek(2, 1)

                    self._seek(5, 1)

                # Add to cache
                if beatmap_hash not in self._beatmap_pointers_cache.keys():
                    self._beatmap_pointers_cache[beatmap_hash] = pointer_beginning_of_map
            return True
        except EOFError:
            # Database ended early, return False
            return False
