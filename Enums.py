from enum import IntEnum, unique


@unique
class GameplayMode(IntEnum):
    STANDARD = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


"""
Things to note about the Mods Enum:
1. NoMod isn't implemented, since I don't think it makes sense (literally the absence of mods)
    ^ Instead, use len(mods) == 0 or something like that.
2. KeyMod isn't implemented either since it's a bitwise combination of other mods, and as such
it doesn't play nice with my bit-offset format.
    ^ Instead, use helper function contains_any_mod(mods, KEY_MODS).
"""


@unique
class Mods(IntEnum):
    NO_FAIL = 0
    EASY = 1
    TOUCH_DEVICE = 2  # Formerly NoVideo
    HIDDEN = 3
    HARD_ROCK = 4
    SUDDEN_DEATH = 5
    DOUBLE_TIME = 6
    RELAX = 7
    HALF_TIME = 8
    NIGHTCORE = 9  # Always used with DT
    FLASHLIGHT = 10
    AUTOPLAY = 11
    SPUNOUT = 12
    AUTOPILOT = 13  # Relax2 in the wiki
    PERFECT = 14
    KEY4 = 15
    KEY5 = 16
    KEY6 = 17
    KEY7 = 18
    KEY8 = 19
    FADE_IN = 20
    RANDOM = 21  # Mania mod
    CINEMA = 22  # LastMod in the wiki
    TARGET_PRACTICE = 23
    KEY9 = 24
    COOP = 25
    KEY1 = 26
    KEY3 = 27
    KEY2 = 28
    SCORE_V2 = 29
    MIRROR = 30


KEY_MODS = {Mods.KEY4, Mods.KEY5, Mods.KEY6, Mods.KEY7, Mods.KEY8}
AUTO_MODS = {Mods.RELAX, Mods.AUTOPILOT, Mods.AUTOPLAY, Mods.CINEMA}

MANIA_UNRANKED_MODS = {Mods.RANDOM, Mods.COOP, Mods.KEY1, Mods.KEY2, Mods.KEY3}
ALL_UNRANKED_MODS = {Mods.TARGET_PRACTICE, Mods.SCORE_V2}.union(AUTO_MODS, MANIA_UNRANKED_MODS)

DIFFICULTY_INCREASING_MODS = {Mods.HARD_ROCK, Mods.SUDDEN_DEATH, Mods.PERFECT, Mods.DOUBLE_TIME, Mods.NIGHTCORE,
                              Mods.HIDDEN, Mods.FLASHLIGHT}
DIFFICULTY_REDUCING_MODS = {Mods.EASY, Mods.NO_FAIL, Mods.HALF_TIME}
