from DBWriter import DBWriter


class CollectionDBWriter(DBWriter):
    def __init__(self, filename: str, overwrite: bool = False):
        super().__init__(filename, overwrite)

        self.collections = []

    def commit(self):
        if self.db_version is None:
            raise ValueError("No DB Version Specified!")

        super()._write_db_version()
        self._write_int(len(self.collections))

        for collection in self.collections:
            self._write_string(collection.name)
            self._write_int(collection.num_beatmaps)

            for map_hash in collection.beatmap_hashes:
                self._write_string(map_hash)
