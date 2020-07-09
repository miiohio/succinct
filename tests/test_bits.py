from bitarray import bitarray

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from succinct.bits import popcount, select, RANK_IN_BYTE, SELECT_IN_BYTE


@given(st.binary(min_size=8, max_size=8))
@settings(max_examples=1000)
def test_popcount(bb: bytes) -> None:
    manual_popcount = sum(bin(b).count("1") for b in bb)
    assert popcount(bb) == manual_popcount


@pytest.mark.parametrize(
    "b", range(0, 255)
)
def test_select_in_byte(b: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([b]))
    cur_rank = 0

    for i, bit in enumerate(bits):
        if bit:
            assert SELECT_IN_BYTE[256 * cur_rank + b] == i
            cur_rank += 1


@given(st.binary(min_size=8, max_size=8))
@settings(max_examples=5000)
def test_select(bb: bytes) -> None:
    bits = bitarray()
    bits.frombytes(bb)

    cur_rank = 0
    for i, b in enumerate(bits):
        if b:
            assert select(bb, cur_rank) == i
            cur_rank += 1


@pytest.mark.parametrize(
    "b", range(0, 255)
)
def test_rank_in_byte(b: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([b]))

    for i in range(len(bits)):
        assert RANK_IN_BYTE[256 * i + b] == sum(bits[0:(i + 1)])
