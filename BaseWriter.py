import os.path
from lzma import compress
from struct import pack


class BaseWriter:
    def __init__(self, filename: str, overwrite: bool):
        if not overwrite and os.path.isfile(filename):
            raise FileExistsError("overwrite=False")
        self.__file = open(filename, 'wb')

    def _write_lzma(self, data: bytes):
        self.__file.write(compress(data))

    def _write_uleb128(self, val: int):
        self.__file.write(self.__parse_uleb128(val))

    def _write_string(self, s: str):
        # Seems like the 0x00-terminated string isn't actually used in practice (correct me if wrong)
        # LOL i'm wrong
        # this is still commented out tho because apparently some of osu! like searching can't handle the 0x00 thing...
        # if s == '':
        #     self._write_byte(0x00)
        #     return

        b = bytearray()
        b.append(0x0b)

        # UTF-8 has no big/little endianness.
        str_utf8 = s.encode("utf-8")
        b.extend(self.__parse_uleb128(len(str_utf8)))
        b.extend(str_utf8)
        self.__file.write(b)

    def _write_single(self, val: float):
        self.__file.write(pack('<f', val))

    def _write_double(self, val: float):
        self.__file.write(pack('<d', val))

    def _write_bool(self, val: bool):
        self.__file.write(pack('<?', val))

    def _write_byte(self, val: int):
        self.__file.write(pack('<B', val))

    def _write_short(self, val: int):
        self.__file.write(pack('<H', val))

    def _write_int(self, val: int):
        self.__file.write(pack('<I', val))

    def _write_long(self, val: int):
        self.__file.write(pack('<Q', val))

    def _tell(self) -> int:
        return self.__file.tell()

    def _seek(self, pos: int, mode: int = 0):
        self.__file.seek(pos, mode)

    def close(self):
        if not self.__file.closed:
            self.__file.close()

    # def __del__(self):
    #     self.close()

    @staticmethod
    def __parse_uleb128(val: int) -> bytearray:
        b = bytearray()

        first_iter = True
        while first_iter or val != 0:
            first_iter = False

            cur = 0b01111111 & val
            val = val >> 7
            if val != 0:
                cur = cur | 0b10000000
            b.append(cur)

        return b
