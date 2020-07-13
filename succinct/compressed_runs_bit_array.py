from typing import Iterator, Optional

from bitarray import bitarray

from succinct.elias_fano_bit_array import EliasFanoBitArray


class CompressedRunsBitArray:
    def __init__(
        self,
        bit_array: bitarray,
        *,
        num_lower_bits: Optional[int] = None
    ) -> None:
        if len(bit_array) != 0:
            self._first_bit: Optional[bool] = bit_array[0]
        else:
            self._first_bit = None

        # Calculate the lengths of the runs
        zeros_bit_array = bitarray()
        ones_bit_array = bitarray()

        for i in range(len(bit_array)):
            if i == 0 or bit_array[i - 1] != bit_array[i]:
                # New run starts here
                if bit_array[i]:
                    ones_bit_array.append(True)
                else:
                    zeros_bit_array.append(True)
            else:
                # Continuing a run
                if bit_array[i]:
                    ones_bit_array.append(False)
                else:
                    zeros_bit_array.append(False)

        zeros_bit_array.append(True)
        ones_bit_array.append(True)

        self._zeros_poppy = EliasFanoBitArray(zeros_bit_array, num_lower_bits=num_lower_bits)
        self._ones_poppy = EliasFanoBitArray(ones_bit_array, num_lower_bits=num_lower_bits)

        assert len(self) == len(bit_array)

    def __len__(self) -> int:
        if self._first_bit is None:
            return 0
        return len(self._zeros_poppy) + len(self._ones_poppy) - 2

    def __iter__(self) -> Iterator[bool]:
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, i: int) -> bool:
        if self._first_bit is None:
            raise IndexError("CompressedRunsBitArray is empty.")
        return self.select(max(0, self.rank(i) - 1)) == i

    def rank(self, i: int) -> int:
        if self._first_bit is None:
            raise IndexError("CompressedRunsBitArray is empty.")
        max_rank_ones = len(self._ones_poppy)
        low = 0
        high = max_rank_ones - 2

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self.select(mid) - 1
            if mid_val < i:
                low = mid + 1
            elif mid_val > i:
                high = mid - 1
            else:
                return mid
        return low

    def rank_zero(self, i: int) -> int:
        if self._first_bit is None:
            raise IndexError("CompressedRunsBitArray is empty.")
        max_rank_zeros = len(self._zeros_poppy)
        low = 0
        high = max_rank_zeros - 2

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self.select_zero(mid) - 1
            if mid_val < i:
                low = mid + 1
            elif mid_val > i:
                high = mid - 1
            else:
                return mid
        return low

    def select(self, rank: int) -> int:
        if self._first_bit is None:
            raise IndexError("CompressedRunsBitArray is empty.")
        if self._first_bit:
            return rank + self._zeros_poppy.select(self._ones_poppy.rank(rank) - 1)
        else:
            return rank + self._zeros_poppy.select(self._ones_poppy.rank(rank))

    def select_zero(self, rank_zero: int) -> int:
        if self._first_bit is None:
            raise IndexError("CompressedRunsBitArray is empty.")
        if self._first_bit:
            return rank_zero + self._ones_poppy.select(self._zeros_poppy.rank(rank_zero))
        else:
            return rank_zero + self._ones_poppy.select(self._zeros_poppy.rank(rank_zero) - 1)
