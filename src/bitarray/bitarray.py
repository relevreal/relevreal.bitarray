from bitarray.basearray import setbit, setbitslice
from bitarray.basearray import BaseArray


class BitArray(BaseArray):
    buffer_func = bytearray

    def __setitem__(self, key: int | slice, value: int) -> None:
        if isinstance(key, slice):
            ones_balance = setbitslice(self._bytes, key, memoryview(value), self._n_bits)
            self._n_filled += ones_balance
            return None
            
        if key >= self._n_bits:
            raise IndexError("bit array index out of range")

        if value != 0 and value != 1:
            raise ValueError("It is a bit array, value can only be set to 0 or 1.")

        ones_balance = setbit(self._bytes, key, value)
        self._n_filled += ones_balance
        return None
