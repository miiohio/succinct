from typing import List

from succinct.permutation import Permutation

from hypothesis import given, settings, example
from hypothesis import strategies as st


@given(
    st.integers(min_value=1, max_value=50)
    .map(lambda x: list(range(x))).flatmap(st.permutations)
)
@settings(max_examples=5000)
@example(values=[0, 1])
@example(values=[3, 2, 1, 0])
@example(values=[2, 8, 1, 4, 5, 6, 9, 10, 12, 14, 13, 15, 11, 0, 3, 7])
def test_permutation_example(values: List[int]) -> None:
    permutation = Permutation(values)

    for i, value in enumerate(values):
        assert permutation.index_of(value) == i
        assert permutation[i] == value
