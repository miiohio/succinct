from bitarray import bitarray
import math
from typing import Iterator

from succinct.poppy import Poppy


class EliasFano:
    def __init__(self, values: Iterator[int], *, num_values: int, max_value: int) -> None:
        """
        Compressed representation of a monotonically-increasing sequence of
        nonnegative integers.
        """

        # Number of bits needed to store the largest value.
        w = math.ceil(math.log2(max(1, max_value)))

        # Number of lower-order bits of each value to store in the lower
        # bit vector.
        num_lower_bits = math.floor(max_value / num_values)
        self._num_lower_bits = num_lower_bits
        if num_lower_bits != 0:
            self._lower_bits = bitarray()
        else:
            self._lower_bits = None

        # Number of higher-order bits of each value to store in the upper bit
        # vector.
        self._num_upper_bits = w - num_lower_bits
        self._upper_bits = bitarray()

        previous_value = 0
        for value in values:
            if value > max_value:
                raise ValueError(
                    f"The value '{value}' is larger than the max_value '{max_value}'"
                )
            if value < previous_value:
                raise ValueError(
                    "Values must be non-decreasing. "
                    f"(Found '{previous_value}' followed by '{value}')"
                )

            if self._lower_bits is not None:
                binary_str = f"{value:b}"
                lower_bits_str = binary_str[-num_lower_bits:].rjust(num_lower_bits, '0')
                self._lower_bits.extend(lower_bits_str)

            upper_bits = value >> num_lower_bits
            previous_upper_bits = previous_value >> num_lower_bits
            if previous_value != -1:
                self._upper_bits.extend([False] * max(0, upper_bits - previous_upper_bits))
            self._upper_bits.append(True)

            previous_value = value
        self._upper_bits.append(False)
        self._upper_poppy = Poppy(self._upper_bits)

    def __getitem__(self, key: int) -> int:
        if self._lower_bits is not None:
            lower_offset = key * self._num_lower_bits
            lower = int(self._lower_bits[lower_offset:lower_offset + self._num_lower_bits].to01(), 2)
        else:
            lower = 0

        upper = self._upper_poppy.select(key) - key
        return (upper << self._num_lower_bits) | lower
