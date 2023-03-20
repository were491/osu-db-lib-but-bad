from BaseReader import BaseReader


class DBReader(BaseReader):
    def __init__(self, filename: str):
        super().__init__(filename)

        self.db_version = self._read_int()
