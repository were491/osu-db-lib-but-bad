from typing import Set, Iterable, Union
from Enums import *


def contains_any_mod(mods: Set[Mods], compare: Iterable[Mods]) -> bool:
    for mod in compare:
        if mod in mods:
            return True

    return False


def contains_all_mods(mods: Set[Mods], compare: Iterable[Mods]) -> bool:
    for mod in compare:
        if mod not in mods:
            return False

    return True


def num_bin_digits(val: int) -> int:
    val = abs(val)

    count = 0
    while val != 0:
        count += 1
        val = val >> 1

    return count


def int_to_mods(mods: int) -> set[Mods]:
    mod_list = set()
    for bit_shift in range(num_bin_digits(mods)):
        if (mods >> bit_shift) % 2 == 1:
            mod_list.add(Mods(bit_shift))

    return mod_list


def mods_to_int(mods: Union[Set[Mods], frozenset[Mods]]) -> int:
    mods_int = 0
    for mod in mods:
        mods_int += (1 << mod)  # mod.value if this wasn't an IntEnum

    return mods_int
