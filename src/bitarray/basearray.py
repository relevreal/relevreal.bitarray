from dataclasses import dataclass

from bitarray.utils import list_repr


class BaseArray:
    buffer_func = bytearray

    def __init__(self, initializer=None, n_bits=None):
        if initializer is None:
            self._bytes = self.buffer_func()
            self._n_bits = 0
            self._n_filled = 0
        elif type(initializer) is int:
            n_bytes, rem_bits = divmod(initializer, 8)
            if rem_bits > 0:
                n_bytes += 1
            self._bytes = self.buffer_func(n_bytes)
            self._n_bits = initializer
            self._n_filled = 0
        elif type(initializer) is str:
            if any(c != '0' and c != '1' for c in initializer):
                raise ValueError(f'{self.__class__.__name__} can contain only 1s and 0s')
            n_bytes, rem_bits = divmod(len(initializer), 8)
            if rem_bits > 0:
                n_bytes += 1
            self._bytes = self.buffer_func(int(initializer[i:i+8][::-1], 2) for i in range(0, len(initializer), 8))
            self._n_bits = len(initializer)
            self._n_filled = sum(byte.bit_count() for byte in self._bytes)
        else:
            self._bytes = self.buffer_func(initializer)
            self._n_bits = n_bits if n_bits is not None else len(self._bytes) * 8
            self._n_filled = sum(byte.bit_count() for byte in self._bytes)


    def is_full(self) -> bool:
        if self._n_filled == self._n_bits:
            return True
        return False
    

    @property
    def n_filled(self):
        return self._n_filled    


    def __iter__(self):
        yield from bytes_iter(self._bytes, self._n_bits)


    def __len__(self) -> int:
        return self._n_bits


    def __getitem__(self, key: int | slice) -> int:
        if isinstance(key, slice):
            bitslice = getbitslice(key, self._n_bits)
            bytes_ = self._bytes[bitslice.start_byte:bitslice.end_byte]
            cls = type(self)
            bitstring = ''.join(
                str(bit)
                for bit in bytes_iter(bytes_)
            )[bitslice.start_bit:((bitslice.end_byte - 1) * 8 + bitslice.end_bit):bitslice.step]
            return cls(bitstring)
            
        if key >= self._n_bits:
            raise IndexError(f'{self.__class__.__name__} index out of range')

        return getbit(self._bytes, key)


    def __eq__(self, value) -> bool:
        return self._bytes == value._bytes


    def __and__(self, value):
        return type(self)(
            (
                b1 & b2
                for b1, b2 in zip(self._bytes, value._bytes)
            ),
            n_bits=self._n_bits,
        )

    
    def __or__(self, value):
        return type(self)(
            (
                b1 | b2
                for b1, b2 in zip(self._bytes, value._bytes)
            ),
            n_bits=self._n_bits,
        )


    def __buffer__(self, flags):
        return self._bytes.__buffer__(flags)


    def __repr__(self) -> str:
        bits = list_repr(self)
        cls = self.__class__.__name__
        if len(self) < 6:
            return f'{cls}({bits})'
        return f'{cls}(nb={len(self)}, nf={self._n_filled}, bits={bits})'


    def __str__(self):
        return str([bit for bit in self])


Bytes = bytes | bytearray
Byte = int
Bit = int


@dataclass
class BitSlice:
    start_byte: int
    start_bit: int
    end_byte: int
    end_bit: int
    step: int


def getbit(bytes_: Bytes, key: int) -> Bit:
    byte_idx, bit_idx = get_idxs(key)
    return getbytesbit(bytes_, byte_idx, bit_idx)


def getbitslice(key: slice, n_bits: int) -> BitSlice:
    indices = key.indices(n_bits)
    start_byte, start_bit = divmod(indices[0], 8)
    end_byte, end_bit = divmod(indices[1], 8)
    step = indices[2] or 1
    return BitSlice(start_byte, start_bit, end_byte + 1, end_bit, step)


def setbit(bytes_: Bytes, key: int, value: Bit) -> int:
    byte_idx, bit_idx = get_idxs(key)
    byte = bytes_[byte_idx]
    new_byte, ones_balance = setbytebit(byte, bit_idx, value)
    bytes_[byte_idx] = new_byte
    return ones_balance
    
    
def setbitslice(bytes_: Bytes, key: slice, value: Bytes, n_bits: int) -> int:
    indices = key.indices(n_bits)
    step = indices[2] or 1
    orig_byte = bytes_[0]
    value_byte = value[0]
    curr_orig_byte_idx = 0
    curr_value_byte_idx = 0
    ones_balance = 0
    for value_bit_idx, orig_bit_idx in enumerate(range(indices[0], indices[1], step)):
        value_byte_idx, value_bit_idx = get_idxs(value_bit_idx)
        orig_byte_idx, orig_bit_idx = get_idxs(orig_bit_idx)
        if curr_orig_byte_idx < orig_byte_idx:
            bytes_[curr_orig_byte_idx] = orig_byte
            curr_orig_byte_idx = orig_byte_idx
            orig_byte = bytes_[curr_orig_byte_idx]
        if curr_value_byte_idx < value_byte_idx:
            curr_value_byte_idx = value_byte_idx
            value_byte = value[curr_value_byte_idx]
        new_bit_value = getbytebit(value_byte, value_bit_idx)
        orig_byte, ones_changed = setbytebit(orig_byte, orig_bit_idx, new_bit_value)
        ones_balance += ones_changed
    bytes_[curr_orig_byte_idx] = orig_byte
    return ones_balance


def setbytebit(byte: Byte, bit_idx: int, value: Bit) -> tuple[Byte, int]:
    curr_value = getbytebit(byte, bit_idx)
    ones_balance = 0
    if value == 1 and curr_value == 0:
        # make mask: [0, 0, 1, 0, 0, 0, ...]
        #                   |
        #               bit to set
        byte |= make_set_mask(bit_idx)
        ones_balance = 1 
    if value == 0 and curr_value == 1:
        # make mask: [1, 1, 0, 1, 1, 1, ...]
        #                   |
        #              bit to clear
        byte &= make_clear_mask(bit_idx)
        ones_balance = -1
    return (byte, ones_balance)


def get_idxs(key: int) -> tuple[int, int]:
    return divmod(key, 8)


def getbytesbit(bytes_: Bytes, byte_idx: int, bit_idx: int) -> Bit:
    byte = bytes_[byte_idx]
    return getbytebit(byte, bit_idx)


def getbytebit(byte: Byte, bit_idx: int) -> Bit:
    # Check if bit is set
    # Need to shift bits because bitarray[0] is actually
    # most significant bit in the first array byte
    # bit = byte & (1 << (7 - bit_idx))
    bit = 1 & (byte >> bit_idx)
    return bit


def byte_iter(byte: Byte, n_bits: int = 8):
    mask = 1
    for i in range(n_bits):
        # if first bit do not bit shift
        if i > 0:
            mask <<= 1
        yield 1 if byte & mask else 0


def bytes_iter(bytes_: Bytes, n_bits: int | None = None):
    bits_left = n_bits if n_bits is not None else len(bytes_) * 8
    for byte in bytes_:
        take_n_bits = 8 if bits_left > 8 else bits_left
        yield from byte_iter(byte, take_n_bits)
        bits_left -= take_n_bits 


def make_set_mask(bit_idx: int) -> Byte:
    return (1 << bit_idx)


def make_clear_mask(bit_idx: int) -> Byte:
    return 255 - (1 << bit_idx)
