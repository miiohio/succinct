from typing import Optional, Iterator, List

from bitarray import bitarray


class RunLengthEncodedBitArray:
    def __init__(self, bit_array: bitarray) -> None:
        prev_value = False
        self._run_starts: List[int] = []
        self._run_lengths: List[int] = []

        for i in range(len(bit_array)):
            if bit_array[i] != prev_value:
                if prev_value:
                    self._run_lengths.append(i - self._run_starts[-1])
                else:
                    self._run_starts.append(i)
            prev_value = bit_array[i]

        if len(self._run_lengths) < len(self._run_starts):
            self._run_lengths.append(len(bit_array) - self._run_starts[-1])

        self._size = len(bit_array)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[bool]:
        for i in range(len(self)):
            yield self[i]

    def _get_run(self, i: int) -> Optional[int]:
        if not self._run_starts:
            return None

        low = 0
        high = len(self._run_starts) - 1

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._run_starts[mid]
            if mid_val < i:
                low = mid + 1
            elif mid_val > i:
                high = mid - 1
            else:
                break

        if low > high:
            mid = high

        if mid < 0:
            mid = (-mid) - 1

        if self._run_starts[mid] <= i and i - self._run_starts[mid] < self._run_lengths[mid]:
            return mid
        else:
            return None

    def _run_contains_index(self, run_id: int, index: int) -> bool:
        return self._run_starts[run_id] <= index and index - self._run_starts[run_id] < self._run_lengths[run_id]

    def __getitem__(self, i: int) -> bool:
        if not (0 <= i < self._size):
            raise IndexError(f"Index out of bounds: {i}")
        return self._get_run(i) is not None

    def rank(self, i: int) -> int:
        run = self._get_run(i)
        rank_sum = 0
        for j in range(len(self._run_starts)):
            if self._run_starts[j] <= i and i - self._run_starts[j] >= self._run_lengths[j]:
                rank_sum += self._run_lengths[j]
            else:
                break

        if run is not None:
            rank_sum += i - self._run_starts[run] + 1

        return rank_sum

    def rank_zero(self, i: int) -> int:
        return i - self.rank(i) + 1

    def select(self, rank: int) -> int:
        low = 0
        high = len(self) - 1

        while low <= high:
            mid = (low + high) // 2
            rz = self.rank(mid)
            if self[mid] and rz == rank + 1:
                return mid
            elif rz <= rank:
                low = mid + 1
            else:
                high = mid - 1
        return -1

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
