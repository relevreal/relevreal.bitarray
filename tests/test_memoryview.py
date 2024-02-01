import pytest

from bitarray.bitarray import BitArray
from bitarray.memoryview import MemoryView


def test_memoryview_2d_ok():
    ba = BitArray('111111000000')
    mv = MemoryView(ba, shape=[2, 6])
    assert mv[0, 0] == 1
    assert ba[0] == 1

    assert mv[0, 5] == 1
    assert ba[5] == 1

    assert mv[1, 0] == 0
    assert ba[6] == 0

    assert mv[1, 1] == 0
    assert ba[7] == 0

    assert mv[1, 5] == 0
    assert ba[11] == 0

    assert mv[-1, -1] == 0

    assert mv[-2, 0] == 1

    mv[0, 0] = 0
    assert mv[0, 0] == 0
    assert ba[0] == 0

    mv[0, 5] = 0
    assert mv[0, 5] == 0
    assert ba[5] == 0

    mv[1, 0] = 1
    assert mv[1, 0] == 1
    assert ba[6] == 1

    mv[1, 1] = 1
    assert mv[1, 1] == 1
    assert ba[7] == 1

    mv[1, 5] = 1
    assert mv[1, 5] == 1
    assert ba[11] == 1

    mv[-1, -1] = 1
    assert mv[-1, -1] == 1
    mv[-2, 0] = 0
    assert mv[-2, 0] == 0

    

def test_memoryview_3d_ok():
    ba = BitArray('111111000000')
    mv = MemoryView(ba, shape=[2, 2, 3])
    assert mv[0, 0, 0] == 1
    assert mv[0, 1, 2] == 1
    assert mv[1, 1, 0] == 0
    assert mv[1, 1, 2] == 0


def test_memoryview_fail():
    ba = BitArray('111111000000')
    mv = MemoryView(ba, shape=[2, 6])
    with pytest.raises(IndexError) as err:
        _ = mv[2, 6]
    assert str(err.value) == 'one of the dimensions is out of bounds'


def test_memoryview_tolist():
    ba = BitArray('111111000000')
    mv = MemoryView(ba, shape=[2, 6])
    ba_list = mv.tolist()
    expected = [
        [1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0],
    ]
    assert ba_list == expected

    mv = MemoryView(ba, shape=[2, 2, 3])
    ba_list = mv.tolist()
    expected = [
        [
            [1, 1, 1], 
            [1, 1, 1],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
        ],
    ]
    assert ba_list == expected
