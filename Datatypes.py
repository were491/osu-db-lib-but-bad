from dataclasses import dataclass
from typing import Union, Optional
from Enums import GameplayMode, Mods


"""
So the thing is that even though the wiki calls beatmaps for the
scores.db, osu!.db, and collection.db the same thing,
they're actually extremely different. So, I mapped it as such:
osu!.db -> BeatmapMetadata, TimingPoint
collection.db -> Collection
scores.db -> ScoreBeatmap, Score
.osr -> Score
"""


@dataclass(frozen=True, order=True)
class TimingPoint:
    """A timing point, ordered by bpm, offset, and red lines < green lines."""
    bpm: float  # If inherited, this is an SV multiplier of -100 / bpm.
    offset: float
    inherited: bool  # Read and green lines


@dataclass
class BeatmapMetadata:
    """Stores information about a beatmap."""
    # Meta-metadata
    size_of_entry: Optional[int]  # None if db_version >= 20191106
    last_modification_time: int
    is_osz2_format: bool
    map_folder: str  # Relative to Songs dir

    # mp3 info
    song_artist: str
    song_artist_unicode: str
    song_title: str
    song_title_unicode: str
    song_source: str
    song_tags: str
    font_used_for_song_title: str  # Don't even ASK me what this is for.
    mp3_name: str

    # Beatmap metadata (doesn't affect gameplay)
    creator: str
    difficulty: str
    difficulty_id: int
    beatmap_hash: str  # Just the difficulty itself, not the whole set.
    beatmap_filename: str  # Just the difficulty itself, not the whole set.
    status: int
    beatmap_id: int  # Refers to the entire set.
    thread_id: int  # Ranking discussion forum thread? Same as Difficulty ID in modern versions.
    drain_time: int  # In sec, not ms like total_time and preview_time
    total_time: int
    preview_timestamp: int
    intended_gameplay_mode: GameplayMode  # See last tab of song setup
    online_offset_ms: int

    # Honestly, I don't know why this is in a separate category, but it just feels right.
    num_circles: int
    num_sliders: int
    num_spinners: int

    # Diff. settings
    approach_rate: Union[int, float]  # byte before 20140609
    circle_size: Union[int, float]  # byte before 20140609
    hp_drain: Union[int, float]  # byte before 20140609
    overall_difficulty: Union[int, float]  # byte before 20140609
    slider_velocity: float
    stack_leniency: float
    mania_scroll_speed: int

    star_ratings_std: dict[frozenset[Mods], float]
    star_ratings_taiko: dict[frozenset[Mods], float]
    star_ratings_ctb: dict[frozenset[Mods], float]
    star_ratings_mania: dict[frozenset[Mods], float]

    timing_points: tuple[TimingPoint]

    # Local info
    highest_grade_std: int
    highest_grade_taiko: int
    highest_grade_ctb: int
    highest_grade_mania: int
    local_offset_ms: int
    is_song_unplayed: bool
    last_played: int
    last_checked_against_osu_repo: int  # For updating?
    user_ignored_beatmap_hitsounds: bool
    user_ignored_beatmap_skin: bool
    user_disabled_storyboard: bool
    user_disabled_video: bool
    visual_override: bool  # I have no idea what this means.

    # Cursed
    unknown_short_value: Optional[int]  # None if db_version >= 20140609.
    last_modification_time_cursed: int


@dataclass(order=True)
class Collection:
    """Represents a collection of maps, with name, number of maps, and map MD5 hashes."""
    name: str
    num_beatmaps: int
    beatmap_hashes: set[str]


# TODO: custom sort order?
@dataclass(order=True)
class Score:
    """Represents a score attained on a beatmap."""
    # Metadata
    replay_version: int  # Kinda like DB version
    replay_hash: str
    beatmap_hash: str
    player_name: str
    timestamp: int
    online_score_id: int

    # About the score
    mode_played: GameplayMode
    mods_used: set[Mods]
    score_earned: int
    max_attained_combo: int
    perfect_combo: bool

    num_300s: int
    num_100s: int
    num_50s: int
    num_misses: int
    num_gekis: int  # Geki = 300 for an entire combo
    num_katus: int  # Katu (Katsu?) = 100 for an entire combo
    tp_accuracy_total: Optional[int]  # "Additional mod information" on site


@dataclass
class ScoreBeatmap:
    """Contains all Scores for a beatmap."""
    beatmap_hash: str
    num_scores: int
    scores: list[Score]
