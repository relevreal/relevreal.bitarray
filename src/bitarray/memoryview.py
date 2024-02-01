import copy
from operator import mul
from functools import reduce
from typing import Sequence
from itertools import batched

from bitarray.basearray import BaseArray, getbit, setbit, getbitslice, bytes_iter


class MemoryView:
    def __init__(self, bitarray: BaseArray, shape: Sequence[int] | None = None) -> None:
        self._memoryview = memoryview(bitarray)
        self.length = len(bitarray)
        self.caster = Caster(len(bitarray), shape) if shape is not None else None


    def cast(self, shape: list[int]):
        mv = copy.copy(self)
        mv.caster = Caster(mv.length, shape)
        return mv


    def __getitem__(self, key: int) -> int:
        if isinstance(key, int):
            return getbit(self._memoryview, key)
        if isinstance(key, tuple):
            if self.caster is None:
                raise ValueError('key cannot be a tuple')
            bit_idx = self.caster.cast(key)
            return getbit(self._memoryview, bit_idx)
        raise ValueError(f'unknown key type{type(key) ({key})}')
    

    def __setitem__(self, key: int, value: int):
        if isinstance(key, int):
            setbit(self._memoryview, key, value)
        elif isinstance(key, tuple):
            if self.caster is None:
                raise ValueError('key cannot be a tuple')
            bit_idx = self.caster.cast(key)
            setbit(self._memoryview, bit_idx, value)
        else:
            raise ValueError(f'unknown key type{type(key) ({key})}')

    
    def tolist(self):
        if self.caster.shape:
            return self._generate_shape_slices(self.caster.shape[1:], self.length)
        return list(bytes_iter(self._memoryview, self.length))


    def _generate_shape_slices(self, shape: Sequence[int], length: int):
        if len(shape) == 1:
            return [
                list(batch)
                for batch in batched(bytes_iter(self._memoryview, length), shape[0])
            ]
        else:
            batches = self._generate_shape_slices(shape[1:], length)
            return [
                list(batch)
                for batch in batched(batches, shape[0])
            ]
            


class Caster:
    def __init__(self, length: int, shape: Sequence[int]):
        if length != reduce(mul, shape, 1):
            raise ValueError(f'wrong shape, {shape} doesn\'t cover array of length {length}')
        l = length
        self.accumulator = tuple(l := l // s for s in shape)
        self.lenght = length
        self.shape = shape


    def cast(self, indices: Sequence[int]):
        if any(idx >= dim for idx, dim in zip(indices, self.shape)):
            raise IndexError('one of the dimensions is out of bounds')
        index = sum(i * a for i, a in zip(indices, self.accumulator))
        return index
