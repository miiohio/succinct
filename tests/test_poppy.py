import math
import random
from typing import Callable, List

import pytest
from bitarray import bitarray
from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis import strategies as st

from succinct.bits import popcount
from succinct.poppy import Poppy


@given(
    initial_value_block_0 = st.integers(min_value=0, max_value=512),
    initial_value_block_1 = st.integers(min_value=0, max_value=512),
    initial_value_block_2 = st.integers(min_value=0, max_value=512),
    add_0 = st.integers(min_value=0, max_value=512),
    add_1 = st.integers(min_value=0, max_value=512),
    add_2 = st.integers(min_value=0, max_value=512)
)
@settings(max_examples=1000)
def test_relative_count(
    initial_value_block_0: int,
    initial_value_block_1: int,
    initial_value_block_2: int,
    add_0: int,
    add_1: int,
    add_2: int,
) -> None:
    assume(initial_value_block_0 + add_0 <= 512)
    assume(initial_value_block_1 + add_1 <= 512)
    assume(initial_value_block_2 + add_2 <= 512)

    initial_values = [
        initial_value_block_0, initial_value_block_1, initial_value_block_2
    ]

    adds = [add_0, add_1, add_2]
    
    packed_count = 0
    for basic_block_index, initial_value in enumerate(initial_values):
        packed_count = Poppy._add_relative_count(
            basic_block_index=basic_block_index,
            packed_relative_counts=packed_count,
            pop_count=initial_value     
        )
    
    for basic_block_index, initial_value in enumerate(initial_values):
        assert Poppy._get_relative_count(
            basic_block_index=basic_block_index,
            packed_relative_counts=packed_count
        ) == initial_value

    for basic_block_index, add in enumerate(adds):
        packed_count = Poppy._add_relative_count(
            basic_block_index=basic_block_index,
            packed_relative_counts=packed_count,
            pop_count=add     
        )

    for basic_block_index, (initial_value, add) in enumerate(zip(initial_values, adds)):
        assert Poppy._get_relative_count(
            basic_block_index=basic_block_index,
            packed_relative_counts=packed_count
        ) == initial_value + add


@pytest.mark.parametrize(
    "byte_value", [42, 255]
)
@pytest.mark.parametrize(
    "num_bytes", [16, (1 << 10), (1 << 29) + 8, ((1 << 29) + 8) * 4]
)
@pytest.mark.slow
def test_l0_layer(byte_value: int, num_bytes: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([byte_value]) * num_bytes)

    # Manually compute the popcount sums here.
    num_popcount_sums = math.ceil(len(bits) / (2**32))
    popcount_sums: List[int] = [0] * num_popcount_sums

    v = memoryview(bits)
    for byte_offset in range(0, len(v), 8):
        popcount_idx = 1 + byte_offset // (2 ** 29)
        if popcount_idx < len(popcount_sums):
            popcount_sums[popcount_idx] += popcount(v[byte_offset:byte_offset + 8])

    for i in range(1, len(popcount_sums)):
        popcount_sums[i] += popcount_sums[i - 1]

    poppy = Poppy(bits)
    assert list(poppy._level_0) == popcount_sums


@pytest.mark.parametrize(
    "byte_value", [42, 255]
)
@pytest.mark.parametrize(
    "num_bytes", [16, (1<<10), (1 << 29) + 8, ((1 << 29) + 8) * 4]
)
@pytest.mark.slow
def test_l1_layer(byte_value: int, num_bytes: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([byte_value]) * num_bytes)

    # Manually compute the popcount sums here.
    level_1_size = math.ceil(len(bits) / 2048)
    level_1: List[int] = [0] *  level_1_size

    v = memoryview(bits)
    for byte_offset in range(0, len(v), 8):
        level_1_idx = 1 + byte_offset // 256
        if level_1_idx < len(level_1):
            level_1[level_1_idx] += popcount(v[byte_offset:byte_offset + 8])

    for byte_offset in range(0, num_bytes, 1<<29):
        level_1_idx = byte_offset // 256
        level_1[level_1_idx] = 0

    for i in range(1, len(level_1)):
        level_1[i] += level_1[i - 1]

    poppy = Poppy(bits)
    # Python will literally asplode if we try to use list equality to compare
    # the two lists.
    for i in range(0, len(level_1)):
        assert poppy._level_1[2 * i] == level_1[i], f"Failed at {i}"


@given(st.binary(min_size=8, max_size=20000))
@settings(max_examples=500)
def test_l2_layer(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)
    bits = bitarray()
    bits.frombytes(bb)
    poppy = Poppy(bits)

    for byte_offset in range(0, len(bb), 64):
        basic_block_idx = (byte_offset % 256) // 64
        if basic_block_idx != 3:
            # Calculate the sum of the bits in the 64-byte block.
            bit_start = 8 * byte_offset
            bit_end = min(len(bits), bit_start + 512)
            expected_pop_count = sum(bits[bit_start:bit_end])

            level_2_idx = (byte_offset // 256) * 2 + 1
            packed_relative_counts = poppy._level_1[level_2_idx]
            actual_pop_count = poppy._get_relative_count(
                basic_block_index=basic_block_idx,
                packed_relative_counts=packed_relative_counts
            )

            assert expected_pop_count == actual_pop_count


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000)
@example(bb=bytes([42] * 136))
def test_rank(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    poppy = Poppy(bits)

    for i in range(len(bits)):
        assert poppy.rank(i) == sum(bits[0:(i + 1)])


@pytest.mark.parametrize(
    "byte_value", [42, 255]
)
@pytest.mark.parametrize(
    "num_bytes,step_size", [
        (16, 1),
        (1<<5, 1),
        (1<<10, 1),
        (1<<15, 1),
        (1<<20, 133),
        ((1<<29) + 8 * 4, 21333)
    ]
)
@pytest.mark.slow
def test_rank_big(byte_value: int, num_bytes: int, step_size: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([byte_value]) * num_bytes)
    poppy = Poppy(bits)

    i = 0
    sum_bits = sum(bits[0:1])
    while i < len(bits):
        assert poppy.rank(i) == sum_bits
        next_i = i + step_size
        partial_sum = sum(
            bits[
                (i + 1):min(next_i + 1, len(bits))
            ]
        )
        i = next_i
        sum_bits += partial_sum


@pytest.mark.slow
def test_rank_boundary() -> None:
    bits = bitarray()
    bits.frombytes(bytes([255]) * ((1<<29) + 32))
    poppy = Poppy(bits)
    i = 1 << 32
    assert poppy.rank(i) == i + 1


@pytest.mark.parametrize(
    "byte_value", [255]
)
@pytest.mark.parametrize(
    "num_bytes", [
        16, (1<<10), (1<<11), (1 << 29) + 8, ((1 << 29) + 8) * 4
    ]
)
@pytest.mark.slow
def test_select_structure(byte_value: int, num_bytes: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([byte_value]) * num_bytes)
    poppy = Poppy(bits)

    for level_0_idx, sampling_answers in enumerate(poppy._select_structure):
        for i, sampling_answer in enumerate(sampling_answers):
            sum_left = poppy._level_0[level_0_idx]
            assert (poppy.rank(sampling_answer + ((1<<32) * level_0_idx)) - sum_left) == (i * 8192 + 1)


@given(st.binary(min_size=8, max_size=10000))
@settings(max_examples=1000)
@example(bb=bytes([42] * 136))
def test_select_poppy(bb: bytes) -> None:
    assume(len(bb) % 8 == 0)

    bits = bitarray()
    bits.frombytes(bb)
    poppy = Poppy(bits)

    select_answers: List[int] = []
    for i in range(len(bits)):
        if bits[i]:
            select_answers.append(i)
    
    for i, pos in enumerate(select_answers):
        assert poppy.select(i) == pos


@pytest.mark.parametrize(
    "byte_value", [42, 255]
)
@pytest.mark.parametrize(
    "num_bytes,step_size", [
        (16, 1),
        (1<<5, 1),
        (1<<10, 1),
        (1<<15, 1),
        (1<<20, 133),
        ((1<<29) + 8 * 4, 21333)
    ]
)
@pytest.mark.slow
def test_select_poppy_big(byte_value: int, num_bytes: int, step_size: int) -> None:
    bits = bitarray()
    bits.frombytes(bytes([byte_value]) * num_bytes)
    poppy = Poppy(bits)

    a = 0
    for i, b in enumerate(bits):
        if b:
            if i % step_size == 0:
                assert poppy.select(a) == i
            a += 1
