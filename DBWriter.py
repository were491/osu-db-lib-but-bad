from BaseWriter import BaseWriter


class DBWriter(BaseWriter):
    def __init__(self, filename: str, overwrite: bool = False):
        super().__init__(filename, overwrite)

        self.db_version = None

    def _write_db_version(self):
        self._write_int(self.db_version)
