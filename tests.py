from OsuDBWriter import OsuDBWriter
from ReplayReader import ReplayReader
from ScoresDBWriter import ScoresDBWriter
from OsuDBReader import OsuDBReader
from ScoresDBReader import ScoresDBReader
from CollectionDBReader import CollectionDBReader


def osu_db_reader_test():
    db = OsuDBReader("test_data/osu!.db")

    print("osu!.db version:", db.db_version)
    print("Folder (mapset) count:", db.folder_count)
    print("Account unlocked?", db.account_unlocked)
    print("When will account be unlocked? (.NET DateTime):", db.date_unlocked)
    print("Player name (empty for guest):", db.player_name)
    print("Number of maps:", db.num_beatmaps)
    print("User perms (0 for guest):", db.user_permissions)

    try:
        # Read one map
        status, maps = db.read_beatmaps_seq(1)
        print("Successfully read first sequential beatmap?", status)
        print("First beatmap data:", maps)

        # Read two maps
        status2, maps2 = db.read_beatmaps_seq(1)
        print("Successfully read first sequential beatmap?", status2)
        print("Second beatmap data:", maps2)

        # Check if map ISN'T in cache
        print("Potato's location in cache:", db.get_beatmap_in_cache("Potato"))

        # Check if map is in cache
        pointer = db.get_beatmap_in_cache(maps2[0].beatmap_hash)
        print("Second map's location in cache:", pointer)

        # Print map seen in cache. Should equal status2/maps2
        status2x2, maps2x2 = db.read_beatmaps(1, pointer)[:2]
        print("Reading the second map again, successful?", status2x2)
        print("Are the two copies of the map equal?", maps2x2 == maps2)

        # Try reading all maps
        status3, maps3 = db.read_all_beatmaps()

        print("Reading all beatmaps, successful?", status3)
        print("What's the 58th map?", maps3[57])
        print("58th map's location in cache:", db.get_beatmap_in_cache(maps3[57].beatmap_hash))

    except Exception as e:
        db.close()
        raise e

    db.close()


def collection_db_reader_test():
    db = CollectionDBReader("test_data/collection.db")

    print("Version:", db.db_version)
    print("Number of Collections:", db.num_collections)
    print("Collection 1:", db.collections[0])

    db.close()


def scores_db_reader_test():
    db = ScoresDBReader("test_data/scores.db")

    print("Num beatmaps with scores:", db.num_beatmaps)

    try:
        status, maps = db.read_beatmaps_seq(1)
        print("Read first map's scores successfully?", status)
        # print("Map's scores:", maps[0])
        print("Map's first score:", maps[0].scores[0])
        print("Map's hash:", maps[0].beatmap_hash)

        status2, maps2 = db.read_beatmaps_seq(5)
        print("Read next 5 maps' scores successfully?", status2)
        print("Second map's first score:", maps2[0].scores[0])
        print("Fourth map's last score:", maps2[2].scores[maps2[2].num_scores - 1])

        pointer = db.get_beatmap_in_cache(maps2[0].beatmap_hash)
        print("Second map location in cache?", pointer)
        print("Hash of second map:", maps2[0].beatmap_hash)
        print("Location of Potato in cache:", db.get_beatmap_in_cache("Potato"))

        status3, maps3 = db.read_beatmaps(1, pointer)[:2]
        print("Re-reading second map successful?", status3)
        print("Re-read from cache map same as original copy?", maps3[0] == maps2[0])

        status4, maps4 = db.read_all_beatmaps()
        print("Reading all scores successful?", status4)
        print("57th beatmap's first score:", maps4[56].scores[0])

        second_to_last_map_ptr = db.get_beatmap_in_cache(maps4[len(maps4) - 2].beatmap_hash)
        status5, maps5 = db.read_beatmaps(3, second_to_last_map_ptr)[:2]
        print("Reading past the end of the DB. Successful?", status5)
        print("What was read:", maps5)

        # The hash 3e57f3caeb75d6fb21d039c3357c7971 corresponds to the second to last map.
        print("Location of the map of hash 3e57f3caeb75d6fb21d039c3357c7971:",
              db.get_beatmap_in_cache("3e57f3caeb75d6fb21d039c3357c7971"))

    except Exception as e:
        db.close()
        raise e

    db.close()


def scores_db_caching_test():
    score_db = ScoresDBReader("test_data/scores.db")

    print(score_db.cache_all_beatmaps())
    print(score_db.get_beatmap_in_cache("Potato"))  # Should be -1
    print(score_db.get_beatmap_in_cache("3e57f3caeb75d6fb21d039c3357c7971"))  # Should be 1508621
    print(score_db.get_beatmap_in_cache("4071f3aea454ce4b94c72cc552eb0599"))  # Should be 3560

    score_db.close()


def osu_db_caching_test():
    osu_db = OsuDBReader("test_data/osu!.db")

    print(osu_db.cache_all_beatmaps())
    print(osu_db.get_beatmap_in_cache("Potato"))  # Should be -1
    print(osu_db.get_beatmap_in_cache("bb73e3a3cfae92476b6be4a8adc4beb6"))  # Should be 2811
    print(osu_db.get_beatmap_in_cache("029eebe9ff6beeee2fe81ffa3c61e9bd"))  # Should be 179598

    osu_db.close()


def osu_db_caching_speed_benchmark():
    db = OsuDBReader("test_data/osu!.db")
    print(db.cache_all_beatmaps())
    db.close()


def osu_db_read_all_speed_benchmark():
    db = OsuDBReader("test_data/osu!.db")
    print(db.read_all_beatmaps()[0])
    db.close()


def scores_db_caching_speed_benchmark():
    score_db = ScoresDBReader("test_data/scores.db")
    print(score_db.cache_all_beatmaps())
    score_db.close()


def scores_db_read_all_speed_benchmark():
    score_db = ScoresDBReader("test_data/scores.db")
    print(score_db.read_all_beatmaps()[0])
    score_db.close()


def real_life_usage_test_1():
    """Reads the first collection and lists all scores in the maps in teh collection."""
    coll_db = CollectionDBReader("test_data/collection.db")
    score_db = ScoresDBReader("test_data/scores.db")

    score_db.cache_all_beatmaps()

    print(coll_db.collections[0], '\n')

    for item in coll_db.collections[0].beatmap_hashes:
        if (ptr := score_db.get_beatmap_in_cache(item)) != -1:
            print('\n', score_db.read_beatmaps(1, ptr)[1])

    coll_db.close()
    score_db.close()


def real_life_usage_test_2():
    """Reads the first map and finds its nomod star rating."""
    osu_db = OsuDBReader("test_data/osu!.db")
    m = osu_db.read_beatmaps_seq(1)[1][0]
    print(m.star_ratings_std[frozenset()])
    osu_db.close()


def real_life_usage_test_3():
    """Reads the fifth map."""
    osu_db = OsuDBReader("test_data/osu!.db")
    m = osu_db.read_beatmaps_seq(5)[1][4]
    print(m)
    osu_db.close()


def read_maps_inside_collection():
    """TimeIt = 9.830914699999994s"""
    coll_db = CollectionDBReader("test_data/collection.db")
    osu_db = OsuDBReader("test_data/osu!.db")

    osu_db.cache_all_beatmaps()

    print(coll_db.collections[0], '\n')

    for item in coll_db.collections[0].beatmap_hashes:
        if (ptr := osu_db.get_beatmap_in_cache(item)) != -1:
            print('\n', osu_db.read_beatmaps(1, ptr)[1][0])

    coll_db.close()
    osu_db.close()


def scores_db_writer_test():
    db = ScoresDBReader("test_data/scores.db")
    db2 = ScoresDBWriter("test_data/scores_test_2.db", True)
    db2.db_version = db.db_version
    db2.write_metadata()
    m = db.read_all_beatmaps()[1]
    db2.write_beatmaps(m[:500])
    db2.write_beatmaps(m[500:])
    db2.close()
    db.close()

    # db = ScoresDBReader("test_data/scores.db")
    # db2 = ScoresDBReader("test_data/scores_test.db")
    # maps1 = db.read_all_beatmaps()
    # maps2 = db2.read_all_beatmaps()
    # print(maps1[1] == maps2[1])


def osu_db_writer_test():
    db = OsuDBReader("test_data/osu!.db")
    db2 = OsuDBWriter("test_data/osu!_test_3.db", True)
    db2.db_version = db.db_version
    db2.folder_count = db.folder_count
    db2.account_unlocked = db.account_unlocked
    db2.date_unlocked = db.date_unlocked
    db2.player_name = db.player_name
    db2.user_permissions = db.user_permissions
    db2.write_metadata()

    maps = db.read_all_beatmaps()
    db2.write_beatmaps(maps[1])
    db2.close()
    return
    # while True:
    #     maps = db.read_beatmaps_seq(500)
    #     db2.write_beatmaps(maps[1])
    #     if maps[0] is False:
    #         break
    # db2.close()


def replay_reader_test():
    replay = ReplayReader("test_data/peppy osu - Camellia feat. Nanahira - Kizuitara Shunkashuutou [Colorful Blend of Four Seasons] (2022-05-21) Osu.osr")
    replay.load()
    print(replay.replay_size)
    print(replay.replay_frames)
