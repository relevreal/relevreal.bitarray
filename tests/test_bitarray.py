import copy

import pytest

from bitarray.bitarray import BitArray
    

def test_bitarray_ok():
    ba = BitArray(16) 
    assert len(ba) == 16

    assert ba[1] == 0
    ba[1] = 1 
    assert ba[1] == 1
    assert ba.n_filled == 1
    assert ba.is_full() is False


def test_bitarray_iterator_ok():
    ba = BitArray(12) 

    for i, b in enumerate(ba):
        assert b == 0
        ba[i] = 1
        assert ba[i] == 1
    
    assert ba.n_filled == 12
    assert ba.is_full()

    for i, b in enumerate(ba):
        assert b == 1
        ba[i] = 0
        assert ba[i] == 0
    
    assert ba.n_filled == 0
    assert ba.is_full() is False


def test_bitarray_initialization_ok():
    ba = BitArray()
    assert len(ba) == 0 
    assert ba._n_filled == 0

    ba = BitArray(12)
    assert len(ba) == 12 
    assert ba._n_filled == 0 

    ba = BitArray('011110000110')
    assert len(ba) == 12
    assert ba._n_filled == 6 

    ba = BitArray(b'abc')
    assert len(ba) == 3 * 8 
    assert ba._n_filled == 10 

    ba = BitArray(range(10))
    assert len(ba) == 10 * 8 
    assert ba._n_filled == 15 


def test_bitarray_initialization_fail():
    with pytest.raises(TypeError) as err:
        _ = BitArray(12.3)
    assert str(err.value) == 'cannot convert \'float\' object to bytearray'

    with pytest.raises(ValueError) as err:
        _ = BitArray('021110')
    assert str(err.value) == 'BitArray can contain only 1s and 0s'

    with pytest.raises(ValueError) as err:
        _ = BitArray([1, 255, 300])
    assert str(err.value) == 'byte must be in range(0, 256)'


def test_bitarray_eq_ok():
    ba_1 = BitArray('1001')
    ba_2 = BitArray('1001')
    ba_3 = BitArray('1110')
    assert ba_1 == ba_2
    assert ba_1 != ba_3


def test_bitarray_copy_ok():
    ba_1 = BitArray('1001')
    ba_2 = copy.copy(ba_1)
    ba_3 = copy.deepcopy(ba_1)
    assert ba_1 == ba_2
    assert ba_1 == ba_3

    ba_1[3] = 0
    assert ba_1 == ba_2
    assert ba_1 != ba_3


def test_bitarray_slicing_ok():
    ba_1 = BitArray('1001001110')

    ba_2 = ba_1[:]
    assert ba_1 == ba_2

    ba_3 = ba_1[:1]
    assert ba_3 == BitArray('1')

    ba_4 = ba_1[:2]
    assert ba_4 == BitArray('10')

    ba_5 = ba_1[1:-1:2]
    assert ba_5 == BitArray('0101')


def test_bitarray_slice_assignment_ok():
    ba_1 = BitArray('1001001111')

    ba_1[1:4] = BitArray('110')
    assert ba_1 == BitArray('1110001111')

    ba_2 = BitArray('11111110000000')
    ba_2[3:11] = BitArray('00001111')
    assert ba_2 == BitArray('11100001111000')


def test_bitarray_str_ok():
    ba = BitArray('1001001111')
    str(ba) == '[1, 0, 0, 1, 0, 0, 1, 1, 1, 1]'


def test_bitarray_repr_ok():
    ba = BitArray('1001001111')
    assert repr(ba) == 'BitArray(nb=10, nf=6, bits=[1, 0, 0, 1, 0, 0, ...])'


def test_bitarray_bitwise_operators_ok():
    ba_1 = BitArray('1001001111')
    ba_2 = BitArray('1111100000')

    result = ba_1 & ba_2
    expected = BitArray('1001000000')
    assert result == expected

    result = ba_1 | ba_2
    expected = BitArray('1111101111')
    assert result == expected
