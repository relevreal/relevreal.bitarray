from bitarray.basearray import BaseArray


class FrozenBitArray(BaseArray):
    buffer_func = bytes

    def __hash__(self) -> int:
        return hash(self._bytes)
