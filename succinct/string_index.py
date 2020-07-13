from collections import defaultdict
from typing import Any, Iterable, Iterator, List, Tuple

from bitarray import bitarray

from succinct.permutation import Permutation
from succinct.rle_bit_array import RunLengthEncodedBitArray


END_CHARACTER = '\0'


def sort_bucket(s: str, bucket: Iterable[int], order: int) -> List[int]:
    """
    https://gist.github.com/prasoon2211/cc3f3d5b43a0885c0e7a
    """
    d: Any = defaultdict(list)
    for i in bucket:
        key = s[i:(i + order)]
        d[key].append(i)
    result: List[int] = []
    for k, v in sorted(d.items()):
        if len(v) > 1:
            result += sort_bucket(s, v, order * 2)
        else:
            result.append(v[0])
    return result


def suffix_array_ManberMyers(s: str) -> List[int]:
    """
    https://gist.github.com/prasoon2211/cc3f3d5b43a0885c0e7a
    """
    return sort_bucket(s, (i for i in range(len(s))), 1)


class StringIndex:
    def __init__(self, strings: List[str]) -> None:
        self._size = len(strings)

        strings_sorted: List[Tuple[str, int]] = []
        for i, s in enumerate(strings):
            strings_sorted.append((s, i))

        s = "".join((x[0] for x in strings_sorted)) + END_CHARACTER
        suffix_array = suffix_array_ManberMyers(s)

        self._alphabet_distinct: List[str] = []
        alphabet_starts: List[int] = []
        for i in range(len(s)):
            if i == 0 or s[suffix_array[i - 1]] != s[suffix_array[i]]:
                self._alphabet_distinct.append(s[suffix_array[i]])
                alphabet_starts.append(i)

        self._alphabet_starts = alphabet_starts

        inverse_suffix_array = [0] * len(suffix_array)

        for i, x in enumerate(suffix_array):
            inverse_suffix_array[x] = i

        # A.K.A. "nextCharIdx"
        psi = [
            inverse_suffix_array[(x + 1) % len(suffix_array)]
            for x in suffix_array
        ]

        self._psi = Permutation(psi)

        # Bit vector that marks psi entries as beginnings of strings.
        starts = bitarray()
        for s, i in strings_sorted:
            starts.append(True)
            starts.extend([False] * (len(s) - 1))
        starts.append(False)

        psi_starts_bitarray = bitarray(len(starts))
        psi_starts_bitarray.setall(False)

        for i, x in enumerate(suffix_array):
            if starts[x]:
                psi_starts_bitarray[i] = True

        self._psi_starts = RunLengthEncodedBitArray(psi_starts_bitarray)

    def __len__(self) -> int:
        return self._size

    def _get_char_at_suffix_array_position(self, position: int) -> str:
        low = 0
        high = len(self._alphabet_starts) - 1

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._alphabet_starts[mid]
            if mid_val < position:
                low = mid + 1
            elif mid_val > position:
                high = mid - 1
            else:
                break

        if low > high:
            mid = high
        return self._alphabet_distinct[mid]

    def __getitem__(self, key: int) -> str:
        if not (0 <= key < self._size):
            raise IndexError(f"Index out of bounds: {key}")
        pos = self._psi_starts.select(key)
        assert pos >= 0
        first_time = True

        result: List[str] = []
        while first_time or not self._psi_starts[pos]:
            first_time = False
            ch = self._get_char_at_suffix_array_position(pos)
            if ch != END_CHARACTER:
                result.append(ch)

            pos = self._psi[pos]

        return "".join(result)

    def __iter__(self) -> Iterator[str]:
        # TODO: This is not the fastest way to iterate over the data structure,
        # but it is at least correct.
        for i in range(len(self)):
            yield self[i]
