from array import array
from itertools import repeat


class BitArray:
    def __init__(self, n_bits):
        n_bytes, reminder = divmod(n_bits, 8)
        if reminder > 0:
            n_bytes += 1 
        self._byte_array = array("B", repeat(0, n_bytes))
        self._n_bits = n_bits
        self._n_filled = 0


    def is_full(self) -> bool:
        if self._n_filled == self._n_bits:
            return True
        return False
    

    def n_filled(self):
        return self._n_filled    


    def __iter__(self):
        self._i = 0
        return self


    def __next__(self):
        if self._i < self._n_bits:
            result = self[self.i]
            self._i += 1
            return result
        raise StopIteration


    def __len__(self):
        return self._n_bits
    

    def __getitem__(self, key):
        if key >= self._n_bits:
            raise IndexError("bit array index out of range")
        byte_idx, bit_idx = divmod(key, 8)
        byte = self._byte_array[byte_idx]
        if byte & (1 << (7 - bit_idx)):
            bit = 1
        else:
            bit = 0
        return bit


    def __setitem__(self, key, value):
        if key >= self._n_bits:
            raise IndexError("bit array index out of range")
        if value != 0 and value != 1:
            raise ValueError("It is a bit array, value can only be set to 0 or 1.")
        byte_idx, bit_idx = divmod(key, 8)
        byte = self._byte_array[byte_idx]
        curr_value = self[key]
        if value == 1 and curr_value != 1:
            byte |= (1 << (7 - bit_idx))
            self._byte_array[byte_idx] = byte
            self.n_filled += 1
        elif value == 0 and curr_value != 0:
            byte &= 255 - (1 << (7 - bit_idx))
            self._byte_array[byte_idx] = byte
            self._n_filled -= 1


    def __repr__(self) -> str:
        repr_str = "BitVector{arr}"
        arr = []
        n_bits = self.n_bits 
        for byte in self._byte_array:
            next_bits = [int(b) for b in bin(byte)[2:].zfill(8)]
            if n_bits >= 8:
                arr += next_bits 
                n_bits -= 8
            else:
                arr += next_bits[:n_bits]
                n_bits = 0
        return repr_str.format(arr=arr)


    def __str__(self) -> str:
        pass