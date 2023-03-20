import os
import sys
import pickle
import shutil
#import win32api, win32con

from Utils import *
from tests import *


# https://stackoverflow.com/questions/7099290/how-to-ignore-hidden-files-using-os-listdir
# def is_hidden(path):
#     attribute = win32api.GetFileAttributes(path)
#     return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)


def delete_unwanted_beatmaps():
    # LOOL deleted exactly 8888 mapsets... this is a good sign
    maps_in_coll_or_with_scores = set()
    collections_db = CollectionDBReader("test_data/collection.db")
    for c in collections_db.collections:
        maps_in_coll_or_with_scores = maps_in_coll_or_with_scores | c.beatmap_hashes
    collections_db.close()

    scores_db = ScoresDBReader("test_data/scores.db")
    score_maps = scores_db.read_all_beatmaps()[1]
    for s in score_maps:
        maps_in_coll_or_with_scores.add(s.beatmap_hash)
    scores_db.close()

    # Set of all maps which have signs of being played/viewed/etc.
    # This is a list of the song's folder (str), not the hash
    maps_touched = set()
    db = OsuDBReader("test_data/osu!.db")
    maps = db.read_all_beatmaps()[1]
    for m in maps:
        # Skip maps with scores or in collections
        if m.beatmap_hash in maps_in_coll_or_with_scores:
            maps_touched.add(m.map_folder)
            continue
        # Checks if NM star rating is high enough for me to care.
        try:
            if m.star_ratings_std[frozenset()] >= 5.3:
                maps_touched.add(m.map_folder)
                continue
        except KeyError:
            # Probably not a osu!std map
            pass
        # Does osu!.db save a ranking?
        if m.highest_grade_std != 9 or m.highest_grade_taiko != 9 or \
                m.highest_grade_ctb != 9 or m.highest_grade_mania != 9:
            maps_touched.add(m.map_folder)
            continue
        # More signs of playing yaay
        if m.local_offset_ms != 0:
            maps_touched.add(m.map_folder)
            continue
        # 216000000000 = 0001-01-01 T 06:00:00.000Z aka unplayed
        if not m.is_song_unplayed or m.last_played != 216000000000:
            maps_touched.add(m.map_folder)
            continue
        # Check for user overrides
        if m.user_ignored_beatmap_hitsounds or m.user_ignored_beatmap_skin or \
                m.user_disabled_storyboard or m.user_disabled_video:
            maps_touched.add(m.map_folder)
            continue
    db.close()

    # Now it's time to iterate through every map folder and check if the date modified of the files inside isn't
    # Sunday, March 10, 2019, since that's apparently when I added a shitton of maps.
    # next(os.walk('.'))[1] lists the immediate subdirectories. using next() only returns the first item in the
    # iterator, i.e., the most immediate (in terms of trees). [1] gets the subdirs only.
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    # TODO: WARNING: this seems to miss nested map dirs
    #  (eg Various+Artists+-+Stream+Practice+Mapsosz\Various Artists - Stream Practice Maps a) and dirs which
    #  incorrectly considered by osu!.db to have a whitespace after the filename
    #  (eg "1449809 Maximum The Hormone - ChuChu Lovely MuniMuni MuraMura PurinPurin Boron Nururu ")
    #  ----------
    #  You can find these exceptions by looping through the touched maps,
    #  then finding which ones aren't in the subdirs.
    parent = 'D:\\_to_organize\\osu!\\Songs'
    subdirs = [item for item in next(os.walk(parent))[1] if not is_hidden(os.path.join(parent, item))]

    num_dirs_deleted = 0

    for subdirectory in subdirs:
        # Of course, skip the maps we said not to delete...
        if subdirectory in maps_touched:
            continue

        # If the modification date of a file in the subdirectory to-be-deleted isn't 3-10-2019 i wanna keep it
        # since it means i downloaded it later
        subdir_path = os.path.join(parent, subdirectory)
        # TODO: Mayybe add recursive searching e.g., if you changed a storyboard
        files_in_subdir = [item for item in next(os.walk(subdir_path))[2] if
                           not is_hidden(os.path.join(subdir_path, item))]

        # Get modification date of each subdirectory and check if it's on 3/10/2019
        # https://stackoverflow.com/questions/237079/how-to-get-file-creation-and-modification-date-times
        # https://www.epochconverter.com/
        found_file_outside_time = False
        for f in files_in_subdir:
            abs_path = os.path.join(subdir_path, f)
            if not 1552197600 < os.path.getmtime(abs_path) < 1552280399:
                found_file_outside_time = True
                break
        if not found_file_outside_time:
            # https://stackoverflow.com/questions/6996603/how-to-delete-a-file-or-folder-in-python
            shutil.rmtree(subdir_path)
            num_dirs_deleted += 1
    print(num_dirs_deleted)
    return


def merge_beatmap_data():
    # db = OsuDBReader("test_data/osu!.db")  # old db
    # db2 = OsuDBReader("new_db_files/osu!.db")  # new db
    db = OsuDBReader("merging_data_back/osu!_old.db")
    db2 = OsuDBReader("merging_data_back/osu!.db")

    try:
        # The new strat here will be
        # to cache all the maps in db,
        # then, if the same map hash exists in the other db,
        # well, it can exist twice...
        # which is a huge problem actually.
        # lol. but i think osu! has the same issue
        # and it probably has the same behavior as me
        # soo i'll hope things work out mostly.
        db.cache_all_beatmaps()

        # Essentially, pull the map data from the old db if possible.
        maps = db2.read_all_beatmaps()[1]
        copy_of_maps = maps.copy()
        for i, m in enumerate(maps):
            if (ptr := db.get_beatmap_in_cache(m.beatmap_hash)) != -1:
                copy_of_maps[i] = db.read_beatmaps(1, ptr)[1][0]
        # print(copy_of_maps[15])
        # print(maps[15])

        new_db = OsuDBWriter("merging_data_back/osu!_new.db", False)
        new_db.db_version = db2.db_version
        new_db.folder_count = db2.folder_count
        new_db.account_unlocked = db2.account_unlocked
        new_db.date_unlocked = db2.date_unlocked
        new_db.player_name = db2.player_name
        new_db.user_permissions = db2.user_permissions
        new_db.write_metadata()
        new_db.write_beatmaps(copy_of_maps)
        new_db.close()

        db.close()
        db2.close()
    except Exception as e:
        db.close()
        db2.close()
        raise e

    return


def nan_is_cringe():
    # two NaNs don't compare equal and this fuckwit put a NaN in his timing points
    db = OsuDBReader("test_data/osu!.db")
    db2 = OsuDBReader("test_data/osu!_test_3.db")

    map1 = db.read_beatmaps(1, 63956033)[1][0]
    map2 = db2.read_beatmaps(1, 63907080)[1][0]

    pts1 = map1.timing_points
    pts2 = map2.timing_points

    for index, val in enumerate(pts1):
        if val != pts2[index]:
            print(val)
            print(pts2[index])

    print(map1)

    # maps1 = db.read_all_beatmaps()[1]
    # maps2 = db2.read_all_beatmaps()[1]
    #
    # for idx, val in enumerate(maps1):
    #     if val != maps2[idx]:
    #         print(db.get_beatmap_in_cache(val.beatmap_hash))  # 63956033
    #         print(db2.get_beatmap_in_cache(maps2[idx].beatmap_hash))  # 63907080


def delete_unwanted_maps_2():
    collections_db = CollectionDBReader("new_stuff_once_again/collection.db")
    osu_db = OsuDBReader("new_stuff_once_again/osu!.db")
    osu_db.cache_all_beatmaps()
    scores_db = ScoresDBReader("new_stuff_once_again/scores.db")
    scores_db.read_all_beatmaps()  # blame my dumbass past self for writing 0x0b 0x00 instead of 0x00

    current_candidates = None
    for coll in collections_db.collections:
        if coll.name == "NewMaps":
            current_candidates = coll.beatmap_hashes
            break

    map_dirs = set()
    for cand in current_candidates:
        # So apparently this is somehow sometimes -1 idek anymore
        # if so i'll remove it i guess
        ptr = osu_db.get_beatmap_in_cache(cand)
        if ptr == -1:
            continue
        m = osu_db.read_beatmaps(1, ptr)[1][0]
        map_dirs.add(m.map_folder)

    for cand in current_candidates:
        # So apparently this is somehow sometimes -1 idek anymore
        # if so i'll remove it i guess
        ptr = osu_db.get_beatmap_in_cache(cand)
        if ptr == -1:
            # these maps wouldn't have been in the candidates anyways
            continue
        m = osu_db.read_beatmaps(1, ptr)[1][0]

        if m.map_folder not in map_dirs:
            continue

        ptr = scores_db.get_beatmap_in_cache(cand)
        if ptr != -1 and scores_db.read_beatmaps(1, ptr)[1][0].num_scores != 0:
            map_dirs.remove(m.map_folder)
            continue

        if m.highest_grade_std != 9 or m.highest_grade_taiko != 9 or \
                m.highest_grade_ctb != 9 or m.highest_grade_mania != 9:
            map_dirs.remove(m.map_folder)
            continue

        if m.local_offset_ms != 0:
            map_dirs.remove(m.map_folder)
            continue

        if not m.is_song_unplayed or m.last_played != 216000000000:
            map_dirs.remove(m.map_folder)
            continue

        # Check for user overrides
        if m.user_ignored_beatmap_hitsounds or m.user_ignored_beatmap_skin or \
                m.user_disabled_storyboard or m.user_disabled_video:
            map_dirs.remove(m.map_folder)
            continue

        if m.intended_gameplay_mode == GameplayMode.STANDARD:
            map_dirs.remove(m.map_folder)
            continue

    # Now it's time to iterate through every map folder and check if the date modified of the files inside isn't
    # Apr 1 2022, since that's apparently when I added a shitton of maps.
    # next(os.walk('.'))[1] lists the immediate subdirectories. using next() only returns the first item in the
    # iterator, i.e., the most immediate (in terms of trees). [1] gets the subdirs only.
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    # TODO: WARNING: this seems to miss nested map dirs
    #  (eg Various+Artists+-+Stream+Practice+Mapsosz\Various Artists - Stream Practice Maps a) and dirs which
    #  incorrectly considered by osu!.db to have a whitespace after the filename
    #  (eg "1449809 Maximum The Hormone - ChuChu Lovely MuniMuni MuraMura PurinPurin Boron Nururu ")
    #  ----------
    #  You can find these exceptions by looping through the touched maps,
    #  then finding which ones aren't in the subdirs.
    parent = 'D:\\fun\\osu!\\Songs'
    subdirs = [item for item in next(os.walk(parent))[1] if not is_hidden(os.path.join(parent, item))]

    num_dirs_deleted = 0

    for subdirectory in subdirs:
        # Of course, skip the maps we said not to delete...
        if subdirectory not in map_dirs:
            continue

        # If the modification date of a file in the subdirectory to-be-deleted isn't 4-1-2022 i wanna keep it
        # since it means i downloaded it later
        subdir_path = os.path.join(parent, subdirectory)
        files_in_subdir = [item for item in next(os.walk(subdir_path))[2] if
                           not is_hidden(os.path.join(subdir_path, item))]

        # Get modification date of each subdirectory and check if it's on 3/10/2019
        # https://stackoverflow.com/questions/237079/how-to-get-file-creation-and-modification-date-times
        # https://www.epochconverter.com/
        found_file_outside_time = False
        for f in files_in_subdir:
            abs_path = os.path.join(subdir_path, f)
            # Apparently windows uses local time not epoch time *facepalm*
            if not 1648774800 < os.path.getmtime(abs_path) < 1648800000:
                found_file_outside_time = True
                break
        if not found_file_outside_time:
            # https://stackoverflow.com/questions/6996603/how-to-delete-a-file-or-folder-in-python
            # shutil.rmtree(subdir_path)
            shutil.move(subdir_path, os.path.join("D:\\fun\\osu!\\Songs_old", subdirectory))
            num_dirs_deleted += 1
    print(num_dirs_deleted)
    return


def fix_scores_db_lol():
    old = ScoresDBReader("new_stuff_once_again/scores.db")
    new = ScoresDBWriter("new_stuff_once_again/scores_fixed.db")
    new.db_version = old.db_version
    new.write_metadata()
    while True:
        maps = old.read_beatmaps_seq(500)
        new.write_beatmaps(maps[1])
        if not maps[0]:
            break
    new.close()


def copy_osu_db():
    db2 = OsuDBReader("merging_data_back/osu!_new.db")
    new_db = OsuDBWriter("merging_data_back/osu!_new_2.db", False)
    new_db.db_version = db2.db_version
    new_db.folder_count = db2.folder_count
    new_db.account_unlocked = db2.account_unlocked
    new_db.date_unlocked = db2.date_unlocked
    new_db.player_name = db2.player_name
    new_db.user_permissions = db2.user_permissions
    new_db.write_metadata()
    while True:
        maps = db2.read_beatmaps_seq(500)
        new_db.write_beatmaps(maps[1])
        if not maps[0]:
            break
    new_db.close()

    # db = OsuDBReader("new_db_files/new_osu!.db")
    # db.cache_all_beatmaps()
    # ptr = db.get_beatmap_in_cache("46ded64c20ba282060fdfd152051f699")
    # maps = db.read_beatmaps(1, ptr)[1]
    # for map in maps:
    #     if map.beatmap_id == 72474:
    #         print(map.beatmap_hash)
    #         print(map.map_folder)
    #         print(map.difficulty)
    #         print()
    # db.close()

    # db = OsuDBReader("new_db_files/new_osu!.db")
    # print(db.db_version)
    # print(db.folder_count)
    # print(db.account_unlocked)
    # print(db.date_unlocked)
    # print(db.player_name)
    # print(db.num_beatmaps)
    # print(db.user_permissions)
    # print(db.cache_all_beatmaps())
    # print(db.read_beatmaps_seq(3))
    # db.close()

    # db = ScoresDBReader("test_data/scores.db")
    # db.cache_all_beatmaps()
    # ptr = db.get_beatmap_in_cache("46ded64c20ba282060fdfd152051f699")
    # diff = db.read_beatmaps(1, ptr)[1][0]
    # for score in diff.scores:
    #     print(score)
    # db.close()


def merge_scores_db():
    # big_db = ScoresDBReader("moreshit/scores_merged.db")
    # new_db = ScoresDBReader("moreshit/scores_old.db")
    # print("old # of maps:", big_db.num_beatmaps)
    # print("new # of maps:", new_db.num_beatmaps)
    #
    # tot_big = 0
    # for score_map in big_db.read_all_beatmaps()[1]:
    #     tot_big += score_map.num_scores
    # print("old # of scores:", tot_big)
    #
    # tot_smol = 0
    # for score_map in new_db.read_all_beatmaps()[1]:
    #     tot_smol += score_map.num_scores
    # print("new # of scores:", tot_smol)
    #
    # return
    small_db = ScoresDBReader("moreshit/scores.db")
    big_db = ScoresDBReader("moreshit/scores_old.db")
    new_db = ScoresDBWriter("moreshit/scores_merged.db", False)
    new_db.db_version = big_db.db_version
    new_db.write_metadata()

    big_db_maps = big_db.read_all_beatmaps()[1]
    small_db_maps = small_db.read_all_beatmaps()[1]

    for score_map in big_db_maps:
        ptr = small_db.get_beatmap_in_cache(score_map.beatmap_hash)
        if ptr != -1:
            score_map_score_hashes = [s.replay_hash for s in score_map.scores]
            small_score_map = small_db.read_beatmaps(1, ptr)[1][0]
            for score in small_score_map.scores:
                if score.replay_hash not in score_map_score_hashes:
                    score_map.scores.append(score)
                    score_map.num_scores += 1
        new_db.write_beatmaps([score_map])

    for score_map in small_db_maps:
        if big_db.get_beatmap_in_cache(score_map.beatmap_hash):
            new_db.write_beatmaps([score_map])
    new_db.close()


def merge_osu_db():
    # db2 = OsuDBReader("moreshit/osu!_old.db")
    # new_db = OsuDBReader("moreshit/osu!_merged.db")
    # print("old # of maps:", db2.num_beatmaps)
    # print("new # of maps:", new_db.num_beatmaps)
    #
    # return
    db = OsuDBReader("moreshit/osu!.db")
    db2 = OsuDBReader("moreshit/osu!_old.db")
    new_db = OsuDBWriter("moreshit/osu!_merged.db", False)
    new_db.db_version = db2.db_version
    new_db.folder_count = db2.folder_count
    new_db.account_unlocked = db2.account_unlocked
    new_db.date_unlocked = db2.date_unlocked
    new_db.player_name = db2.player_name
    new_db.user_permissions = db2.user_permissions
    new_db.write_metadata()
    while True:
        maps = db2.read_beatmaps_seq(500)
        new_db.write_beatmaps(maps[1])
        if not maps[0]:
            break
    while True:
        maps = db.read_beatmaps_seq(500)
        new_maps = []
        for m in maps[1]:
            if db2.get_beatmap_in_cache(m.beatmap_hash) == -1:
                new_maps.append(m)
        new_db.write_beatmaps(new_maps)
        if not maps[0]:
            break
    new_db.close()


def main(args):
    rr = ReplayReader("0a0f13529506729c77f7e9748dba5e3d-131771989442195986.osr")
    rr.load()
    print(rr.replay_frames)
    return


if __name__ == '__main__':
    # import timeit
    # print(timeit.timeit("osu_db_read_all_speed_benchmark()", globals=locals(), number=2) / 2)
    # print(timeit.timeit("osu_db_caching_speed_benchmark()", globals=locals(), number=2) / 2)
    main(sys.argv)
