from bitarray import bitarray
import math
from typing import Iterable


class EliasFano:
    def __init__(self, values: Iterable[int], *, num_values: int, max_value: int) -> None:
        """
        Compressed representation of a monotonically-increasing sequence of
        nonnegative integers.
        """
        
        # Number of bits needed to store the largest value.
        w = math.ceil(math.log2(max_value))

        # Number of lower-order bits of each item to store in the lower
        # bit vector.
        num_lower_bits = math.floor(max_value / num_values)

        self._lower_bits = bitarray(num_lower_bits)
        # for value in values:
        #     for lower_bit in range(num_lower_bits - 1)