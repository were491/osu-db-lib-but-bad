from DBReader import DBReader
from Datatypes import Collection


class CollectionDBReader(DBReader):
    def __init__(self, filename: str):
        super().__init__(filename)

        self.num_collections = self._read_int()
        self.collections = []
        for i in range(self.num_collections):
            name = self._read_string()
            num_beatmaps = self._read_int()

            beatmap_hashes = set()
            for j in range(num_beatmaps):
                beatmap_hashes.add(self._read_string())

            self.collections.append(Collection(
                name,
                num_beatmaps,
                beatmap_hashes
            ))
