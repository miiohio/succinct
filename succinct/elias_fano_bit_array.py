from typing import Iterable, Iterator, Optional

from bitarray import bitarray
from succinct.eliasfano import EliasFano


class EliasFanoBitArray:
    def __init__(
        self,
        bit_array: bitarray,
        *,
        num_lower_bits: Optional[int] = None
    ) -> None:
        # TODO: Just take the Elias-Fano list directly as input. That will avoid
        #       wasteful construction of a bitarray.
        self._size = len(bit_array)

        def _one_bits() -> Iterable[int]:
            for i, b in enumerate(bit_array):
                if b:
                    yield i

        num_one_bits = 0
        for max_one_bit in _one_bits():
            num_one_bits += 1

        self._one_bit_positions: Optional[EliasFano] = EliasFano(
            values=iter(_one_bits()),
            num_values=num_one_bits,
            max_value=max_one_bit,
            num_lower_bits=num_lower_bits
        ) if num_one_bits > 0 else None

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[bool]:
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, i: int) -> bool:
        if self._one_bit_positions is None:
            return False
        low = 0
        high = len(self._one_bit_positions) - 1
        mid = -1

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._one_bit_positions[mid]
            if mid_val < i:
                low = mid + 1
            elif mid_val > i:
                high = mid - 1
            else:
                return True

        return False

    def rank(self, i: int) -> int:
        if self._one_bit_positions is None:
            return 0
        low = 0
        high = len(self._one_bit_positions) - 1

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._one_bit_positions[mid]
            if mid_val < i:
                low = mid + 1
            elif mid_val > i:
                high = mid - 1
            else:
                return mid + 1

        if mid >= 0:
            return high + 1
        raise ValueError(f"Unable to find a bit with rank {i}.")

    def rank_zero(self, i: int) -> int:
        return i - self.rank(i) + 1

    def select(self, rank: int) -> int:
        if self._one_bit_positions is None or rank < 0 or rank >= len(self._one_bit_positions):
            return -1

        return self._one_bit_positions[rank]

    def select_zero(self, rank_zero: int) -> int:
        low = 0
        high = len(self) - 1

        while low <= high:
            mid = (low + high) // 2
            rz = self.rank_zero(mid)
            if (not self[mid]) and rz == rank_zero + 1:
                return mid
            elif rz <= rank_zero:
                low = mid + 1
            else:
                high = mid - 1
        return -1
