from typing import List

from bitarray import bitarray
from succinct.eliasfano import EliasFano

from hypothesis import given, settings, example
from hypothesis import strategies as st


def test_elias_fano_lower_bits() -> None:
    values = [2, 3, 5, 7, 11, 13, 24]
    ef = EliasFano(iter(values), num_values=len(values), max_value=max(values))

    # lower 3 bits of each number
    expected_lower_bits = bitarray('010011101111011101000')
    assert ef._lower_bits == expected_lower_bits


def test_elias_fano_upper_bits() -> None:
    values = [2, 3, 5, 7, 11, 13, 24]
    ef = EliasFano(iter(values), num_values=len(values), max_value=max(values))

    # Unary encoding of the counts of the upper bits of each number.
    #
    # Values in binary:
    #   00010 00011 00101 00111 01011 01101 11000
    #
    # Upper bits (binary):
    #   00 00 00 00 01 01 11
    #
    # Upper bits (decimal):
    #    0  0  0  0  1  1  3
    # Unary encoding:
    #
    #  1   1   1   1   0   1   1   0   0   1   0
    # (0)                 (1)         (2) (3)
    #
    # In other words:
    # - There are four values whose upper bits are decimal 0
    # - There are two values whose upper bits are decimal 1
    # - There are zero values whose upper bits are decimal 2
    # - There is one value whose upper bits are decimal 3
    expected_upper_bits = bitarray('11110110010')
    while len(expected_upper_bits) % 64 != 0:
        expected_upper_bits.append(False)
    assert ef._upper_bits == expected_upper_bits


@given(
    st.lists(
        st.integers(min_value=0, max_value=100), min_size=1, max_size=2000
    ).map(lambda xs: sorted(xs))
)
@settings(max_examples=10000)
@example(values=[0, 1, 2, 3, 4, 5])
@example(values=[2, 3, 4, 5, 6, 7])
@example(values=[2, 3, 5, 7, 11, 13, 24])
@example(values=[5, 5, 5, 5])
def test_elias_fano_lookup(values: List[int]) -> None:
    ef = EliasFano(iter(values), num_values=len(values), max_value=max(values))
    for i, value in enumerate(values):
        assert ef[i] == value
