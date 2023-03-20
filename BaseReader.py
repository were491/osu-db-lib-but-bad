from struct import unpack
from lzma import decompress


class BaseReader:
    def __init__(self, filename: str):
        """Base class for reading osu! file datatypes."""
        with open(filename, 'rb') as f:
            self.__file = f.read()
        self.__data_count = len(self.__file)
        self.__ptr = 0

    def __read_bytes(self, count: int) -> bytes:
        """Reads <count> bytes from data as bytes."""
        if self.__ptr + count > self.__data_count or self.__ptr == self.__data_count:
            raise EOFError("Out of data!")

        data = self.__file[self.__ptr:self.__ptr + count]
        self.__ptr += count

        return data

    def _read_lzma(self, num_bytes: int) -> bytes:
        return decompress(self.__read_bytes(num_bytes))

    def _read_uleb128(self) -> int:
        """Reads a ULEB integer."""
        number = 0
        shift = 0

        while True:
            byte = self.__read_bytes(1)[0]
            if byte < 0b10000000:
                number = number + (byte << shift)
                break

            number = number + (byte - 128 << shift)
            shift += 7

        return number

    def _read_string(self) -> str:
        """Reads an osu!-style string."""
        if self.__read_bytes(1)[0] == 0x00:
            return ''

        num_bytes = self._read_uleb128()
        return self.__read_bytes(num_bytes).decode("utf-8")

    def _read_single(self) -> float:
        return unpack('<f', self.__read_bytes(4))[0]

    def _read_double(self) -> float:
        return unpack('<d', self.__read_bytes(8))[0]

    def _read_bool(self) -> bool:
        return unpack('<?', self.__read_bytes(1))[0]

    def _read_byte(self) -> int:
        return unpack('<B', self.__read_bytes(1))[0]

    def _read_short(self) -> int:
        return unpack('<H', self.__read_bytes(2))[0]

    def _read_int(self) -> int:
        return unpack('<I', self.__read_bytes(4))[0]

    def _read_long(self) -> int:
        return unpack('<Q', self.__read_bytes(8))[0]

    def _seek(self, count: int, mode: int = 0):
        if mode == 0:
            self.__ptr = count
        elif mode == 1:
            self.__ptr += count
        elif mode == 2:
            self.__ptr = self.__data_count + count
        else:
            raise ValueError("Seeking mode is invalid.")

    def _tell(self) -> int:
        return self.__ptr

    def close(self):
        pass
