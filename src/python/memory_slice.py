def to_int(width: int, value):
    """
    Convert a value to an signed integer with the given width.
    """
    if width <= 0:
        raise ValueError("Width must be positive")

    value = int(value) & ((1 << width) - 1)

    if value & (1 << (width - 1)):
        value -= 1 << width

    return value


class MemorySlice:
    """
    A Slice of memory of a given width.
    Lower bits are on the right. The same as we write binary numbers.
    """

    def get_width(self):
        raise NotImplementedError()

    def __init__(self, data):
        # self._data is always signed int.
        self._data = to_int(self.get_width(), data)

    def __int__(self):
        return self._data

    def __hex__(self):
        return hex(self._data)

    def __getitem__(self, s) -> int:
        """
        Get the value at the given index or slice.
        Always return an positive integer.

        Example: 0 is the rightmost (lowest) bit,
        [5:0] returns the rightmost 6 bits
        """
        if isinstance(s, slice):
            if s.step not in (None, 1):
                raise ValueError("Step must be 1 or None")
            if s.start is None:
                start = self.get_width() - 1
            else:
                start = s.start
            if s.stop is None:
                stop = 0
            else:
                stop = s.stop
            if (
                start < 0
                or start >= self.get_width()
                or stop < 0
                or stop >= self.get_width()
            ):
                raise ValueError("Slice out of range")
            if start < stop:
                raise ValueError("Start must be larger than stop")

            mask = ((1 << (start - stop + 1)) - 1) << stop
            return (self._data & mask) >> stop
        else:
            return (self._data >> s) & 1


class MemorySlice32(MemorySlice):
    def get_width(self):
        return 32


class Operand(MemorySlice):
    def get_width(self):
        return self._width

    def __init__(self, data, width=32):
        self._width = width
        super().__init__(data)

    def unsigned(self):
        if self._data < 0:
            return self._data + (1 << self._width)
        else:
            return self._data

    def signed(self):
        return self._data
