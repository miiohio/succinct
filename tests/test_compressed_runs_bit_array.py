from datetime import timedelta
from typing import List

from bitarray import bitarray
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from succinct.compressed_runs_bit_array import CompressedRunsBitArray


def test_compressed_runs_bit_array_rank_example_1a() -> None:
    bits = bitarray('00001111111100101111')
    crba = CompressedRunsBitArray(bits)

    assert crba.rank(0) == 0
    assert crba.rank(1) == 0
    assert crba.rank(2) == 0
    assert crba.rank(3) == 0
    assert crba.rank(4) == 1
    assert crba.rank(5) == 2
    assert crba.rank(6) == 3
    assert crba.rank(7) == 4
    assert crba.rank(8) == 5
    assert crba.rank(9) == 6
    assert crba.rank(10) == 7
    assert crba.rank(11) == 8
    assert crba.rank(12) == 8
    assert crba.rank(13) == 8
    assert crba.rank(14) == 9
    assert crba.rank(15) == 9
    assert crba.rank(16) == 10
    assert crba.rank(17) == 11
    assert crba.rank(18) == 12
    assert crba.rank(19) == 13


def test_compressed_runs_bit_array_rank_example_1b() -> None:
    bits = bitarray('11110000000011010000')
    crba = CompressedRunsBitArray(bits)

    assert crba.rank_zero(0) == 0
    assert crba.rank_zero(1) == 0
    assert crba.rank_zero(2) == 0
    assert crba.rank_zero(3) == 0
    assert crba.rank_zero(4) == 1
    assert crba.rank_zero(5) == 2
    assert crba.rank_zero(6) == 3
    assert crba.rank_zero(7) == 4
    assert crba.rank_zero(8) == 5
    assert crba.rank_zero(9) == 6
    assert crba.rank_zero(10) == 7
    assert crba.rank_zero(11) == 8
    assert crba.rank_zero(12) == 8
    assert crba.rank_zero(13) == 8
    assert crba.rank_zero(14) == 9
    assert crba.rank_zero(15) == 9
    assert crba.rank_zero(16) == 10
    assert crba.rank_zero(17) == 11
    assert crba.rank_zero(18) == 12
    assert crba.rank_zero(19) == 13


def test_compressed_runs_bit_array_rank_example_2a() -> None:
    bits = bitarray('100001111111100101111')
    crba = CompressedRunsBitArray(bits)

    assert crba.rank(0) == 1
    assert crba.rank(1) == 1
    assert crba.rank(2) == 1
    assert crba.rank(3) == 1
    assert crba.rank(4) == 1
    assert crba.rank(5) == 2
    assert crba.rank(6) == 3
    assert crba.rank(7) == 4
    assert crba.rank(8) == 5
    assert crba.rank(9) == 6
    assert crba.rank(10) == 7
    assert crba.rank(11) == 8
    assert crba.rank(12) == 9
    assert crba.rank(13) == 9
    assert crba.rank(14) == 9
    assert crba.rank(15) == 10
    assert crba.rank(16) == 10
    assert crba.rank(17) == 11
    assert crba.rank(18) == 12
    assert crba.rank(19) == 13
    assert crba.rank(20) == 14


def test_compressed_runs_bit_array_rank_example_2b() -> None:
    bits = bitarray('011110000000011010000')
    crba = CompressedRunsBitArray(bits)

    assert crba.rank_zero(0) == 1
    assert crba.rank_zero(1) == 1
    assert crba.rank_zero(2) == 1
    assert crba.rank_zero(3) == 1
    assert crba.rank_zero(4) == 1
    assert crba.rank_zero(5) == 2
    assert crba.rank_zero(6) == 3
    assert crba.rank_zero(7) == 4
    assert crba.rank_zero(8) == 5
    assert crba.rank_zero(9) == 6
    assert crba.rank_zero(10) == 7
    assert crba.rank_zero(11) == 8
    assert crba.rank_zero(12) == 9
    assert crba.rank_zero(13) == 9
    assert crba.rank_zero(14) == 9
    assert crba.rank_zero(15) == 10
    assert crba.rank_zero(16) == 10
    assert crba.rank_zero(17) == 11
    assert crba.rank_zero(18) == 12
    assert crba.rank_zero(19) == 13
    assert crba.rank_zero(20) == 14


def test_compressed_runs_bit_array_select_example_1a() -> None:
    bits = bitarray('00001111111100101111')
    crba = CompressedRunsBitArray(bits)

    assert crba.select(0) == 4
    assert crba.select(1) == 5
    assert crba.select(2) == 6
    assert crba.select(3) == 7
    assert crba.select(4) == 8
    assert crba.select(5) == 9
    assert crba.select(6) == 10
    assert crba.select(7) == 11
    assert crba.select(8) == 14
    assert crba.select(9) == 16
    assert crba.select(10) == 17
    assert crba.select(11) == 18
    assert crba.select(12) == 19


def test_compressed_runs_bit_array_select_example_1b() -> None:
    bits = bitarray('11110000000011010000')
    crba = CompressedRunsBitArray(bits)

    assert crba.select_zero(0) == 4
    assert crba.select_zero(1) == 5
    assert crba.select_zero(2) == 6
    assert crba.select_zero(3) == 7
    assert crba.select_zero(4) == 8
    assert crba.select_zero(5) == 9
    assert crba.select_zero(6) == 10
    assert crba.select_zero(7) == 11
    assert crba.select_zero(8) == 14
    assert crba.select_zero(9) == 16
    assert crba.select_zero(10) == 17
    assert crba.select_zero(11) == 18
    assert crba.select_zero(12) == 19


def test_compressed_runs_bit_array_select_example_2a() -> None:
    bits = bitarray('100001111111100101111')
    crba = CompressedRunsBitArray(bits)

    assert crba.select(0) == 0
    assert crba.select(1) == 5
    assert crba.select(2) == 6
    assert crba.select(3) == 7
    assert crba.select(4) == 8
    assert crba.select(5) == 9
    assert crba.select(6) == 10
    assert crba.select(7) == 11
    assert crba.select(8) == 12
    assert crba.select(9) == 15
    assert crba.select(10) == 17
    assert crba.select(11) == 18
    assert crba.select(12) == 19
    assert crba.select(13) == 20


def test_compressed_runs_bit_array_select_example_2b() -> None:
    bits = bitarray('011110000000011010000')
    crba = CompressedRunsBitArray(bits)

    assert crba.select_zero(0) == 0
    assert crba.select_zero(1) == 5
    assert crba.select_zero(2) == 6
    assert crba.select_zero(3) == 7
    assert crba.select_zero(4) == 8
    assert crba.select_zero(5) == 9
    assert crba.select_zero(6) == 10
    assert crba.select_zero(7) == 11
    assert crba.select_zero(8) == 12
    assert crba.select_zero(9) == 15
    assert crba.select_zero(10) == 17
    assert crba.select_zero(11) == 18
    assert crba.select_zero(12) == 19
    assert crba.select_zero(13) == 20


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000, deadline=None)
@example(bb=bytes([42] * 136))
def test_compressed_runs_bit_array_getitem(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    crba = CompressedRunsBitArray(bits)

    for i in range(len(bits)):
        assert crba[i] == bits[i]


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000, deadline=timedelta(milliseconds=2000))
@example(bb=bytes([42] * 136))
def test_compressed_runs_bit_array_rank(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    crba = CompressedRunsBitArray(bits)

    for i in range(len(bits)):
        assert crba.rank(i) == sum(bits[0:(i + 1)])


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000, deadline=timedelta(milliseconds=2000))
@example(bb=bytes([42] * 136))
def test_compressed_runs_bit_array_rank_zero(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    crba = CompressedRunsBitArray(bits)

    for i in range(len(bits)):
        assert crba.rank_zero(i) == sum(1 - int(b) for b in bits[0:(i + 1)])


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000, deadline=timedelta(milliseconds=500))
@example(bb=bytes([42] * 136))
def test_compressed_runs_bit_array_select(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    crba = CompressedRunsBitArray(bits)

    select_answers: List[int] = []
    for i in range(len(bits)):
        if bits[i]:
            select_answers.append(i)

    for i, pos in enumerate(select_answers):
        assert crba.select(i) == pos


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000, deadline=timedelta(milliseconds=2000))
@example(bb=bytes([42] * 136))
def test_compressed_runs_bit_array_select_zero(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    crba = CompressedRunsBitArray(bits)

    select_zero_answers: List[int] = []
    for i in range(len(bits)):
        if not bits[i]:
            select_zero_answers.append(i)

    for i, pos in enumerate(select_zero_answers):
        assert crba.select_zero(i) == pos
