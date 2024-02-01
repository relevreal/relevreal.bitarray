import copy
import pytest
from bitarray.frozenbitarray import FrozenBitArray
    

def test_frozenbitarray_fail():
    ba = FrozenBitArray(16) 
    assert len(ba) == 16
    assert ba[1] == 0
    with pytest.raises(TypeError) as err:
        ba[1] = 1 
    assert str(err.value) == '\'FrozenBitArray\' object does not support item assignment'


def test_frozenbitarray_iterator_ok():
    ba = FrozenBitArray('1111') 

    for bit in ba:
        assert bit == 1
    
    assert ba.n_filled == 4
    assert ba.is_full()

    ba = FrozenBitArray('0000') 

    for bit in ba:
        assert bit == 0
    
    assert ba.n_filled == 0
    assert ba.is_full() is False


def test_frozenbitarray_initialization_ok():
    ba = FrozenBitArray()
    assert len(ba) == 0 
    assert ba._n_filled == 0

    ba = FrozenBitArray(12)
    assert len(ba) == 12 
    assert ba._n_filled == 0 

    ba = FrozenBitArray('011110000110')
    assert len(ba) == 12
    assert ba._n_filled == 6 

    ba = FrozenBitArray(b'abc')
    assert len(ba) == 3 * 8 
    assert ba._n_filled == 10 

    ba = FrozenBitArray(range(10))
    assert len(ba) == 10 * 8 
    assert ba._n_filled == 15 


def test_frozenbitarray_initialization_fail():
    with pytest.raises(TypeError) as err:
        _ = FrozenBitArray(12.3)
    assert str(err.value) == "cannot convert 'float' object to bytes"

    with pytest.raises(ValueError) as err:
        _ = FrozenBitArray('021110')
    assert str(err.value) == 'FrozenBitArray can contain only 1s and 0s'

    with pytest.raises(ValueError) as err:
        _ = FrozenBitArray([1, 255, 300])
    assert str(err.value) == 'bytes must be in range(0, 256)'


def test_frozenbitarray_eq_ok():
    ba_1 = FrozenBitArray('1001')
    ba_2 = FrozenBitArray('1001')
    ba_3 = FrozenBitArray('1110')
    assert ba_1 == ba_2
    assert ba_1 != ba_3


def test_frozenbitarray_copy_ok():
    ba_1 = FrozenBitArray('1001')
    ba_2 = copy.copy(ba_1)
    ba_3 = copy.deepcopy(ba_1)
    assert ba_1 == ba_2
    assert ba_1 == ba_3


def test_frozenbitarray_slicing_ok():
    ba_1 = FrozenBitArray('10010011')

    ba_2 = ba_1[:]
    assert ba_1 == ba_2

    ba_3 = ba_1[:1]
    assert ba_3 == FrozenBitArray('1')

    ba_4 = ba_1[:2]
    assert ba_4 == FrozenBitArray('10')

    ba_5 = ba_1[1:-1:2]
    assert ba_5 == FrozenBitArray('010')


def test_frozenbitarray_slice_assignment_ok():
    ba_1 = FrozenBitArray('1001001111')
    
    with pytest.raises(TypeError) as err:
        ba_1[1:4] = FrozenBitArray('110')
    assert str(err.value) == '\'FrozenBitArray\' object does not support item assignment'


def test_frozenbitarray_str_ok():
    ba = FrozenBitArray('1001001111')
    str(ba) == '[1, 0, 0, 1, 0, 0, 1, 1, 1, 1]'


def test_frozenbitarray_repr_ok():
    ba = FrozenBitArray('1001001111')
    assert repr(ba) == 'FrozenBitArray(nb=10, nf=6, bits=[1, 0, 0, 1, 0, 0, ...])'


def test_frozenbitarray_bitwise_operators_ok():
    ba_1 = FrozenBitArray('1001001111')
    ba_2 = FrozenBitArray('1111100000')

    result = ba_1 & ba_2
    expected = FrozenBitArray('1001000000')
    assert result == expected

    result = ba_1 | ba_2
    expected = FrozenBitArray('1111101111')
    assert result == expected


def test_frozenbitarray_hash_ok():
    ba_1 = FrozenBitArray('1001001111')
    ba_1_hash= hash(ba_1)
    
    ba_2 = FrozenBitArray('0001001111')
    ba_2_hash= hash(ba_2)

    assert ba_1_hash != ba_2_hash

    d = {
        ba_1: 'ba_1',
        ba_2: 'ba_2',
    }
    assert ba_1 in d
    assert ba_2 in d

    s = set([ba_1, ba_2, ba_1])
    assert ba_1 in s
    assert ba_2 in s
    assert len(s) == 2
