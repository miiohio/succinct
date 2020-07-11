import math
from array import array
from bitarray import bitarray
from typing import List, Optional, Tuple
from typing_extensions import Final

from succinct.bits import popcount, select, RANK_IN_BYTE, SELECT_IN_BYTE


SELECT_SAMPLING_STEP: Final = 8192


class Poppy:
    """
    "Space-efficient, high-performance rank and select structures on
    uncompressed bit sequences" by Zhou, Andersen, and Kaminsky.

    - Supports bit arrays with up to 2^64 bits.

    - Uses 3.25% extra space for rank + 0.39% extra space for select = ~4%.
      Contrast this with other state of the art algorithms that may take
      25-67% extra space for rank, and 10-50% extra space for select.

    - Offers performance comparable to state-of-the-art algorithms. (If
      implemented in C. The Python version may be slower. Shrug!)
    """
    def __init__(self, bit_array: bitarray) -> None:
        self._bit_array = bit_array

        # HACK: For now, pad the bit array until it is a multiple of 8 bytes
        # (64 bits) in length
        while len(self._bit_array) % 64 != 0:
            self._bit_array.append(False)

        self._memory_view = memoryview(bit_array)
        self._level_0, self._level_1 = self._initialize_rank_structure()

        self._select_structure = self._initialize_select_structure()

    def _initialize_rank_structure(self) -> "Tuple[array[int], array[int]]":
        # Need a level 0 entry for every 2**32 bits in the input array.
        level_0_size = math.ceil(len(self._bit_array) / (1 << 32))
        level_0 = array('Q', [0] * level_0_size)

        # How many L1/L2 entries do we need?
        # There is 1 64-bit entry for every 2048 bits in the input.
        # (Equivalently, 2 32-bit entries.)

        level_1_size = 2 * math.ceil(len(self._bit_array) / 2048)
        level_1 = array('L', [0] * level_1_size)

        # Iterate over the input bit array in size of at most 512 bits (64 bytes)
        bit_array_byte_length = len(self._memory_view)

        for byte_offset in range(0, bit_array_byte_length, 8):
            pop_count = popcount(self._memory_view[byte_offset:byte_offset + 8])

            # Update the Level 0 cumulative sum
            level_0_idx = 1 + byte_offset // (1 << 29)
            if level_0_idx < level_0_size:
                level_0[level_0_idx] += pop_count

            # Update the Level 1 cumulative sum.
            level_1_idx = (byte_offset // 256) * 2 + 2
            if level_1_idx < level_1_size:
                level_1[level_1_idx] += pop_count

            # Update the Level 2 non-cumulative relative counts.
            # (But only for basic blocks 0, 1, and 2.  (Skip basic block 3.))
            basic_block_index = (byte_offset % 256) // 64
            if basic_block_index != 3:
                level_2_idx = (byte_offset // 256) * 2 + 1
                packed_relative_counts = level_1[level_2_idx]
                packed_relative_counts = self._add_relative_count(
                    basic_block_index=basic_block_index,
                    packed_relative_counts=packed_relative_counts,
                    pop_count=pop_count
                )
                level_1[level_2_idx] = packed_relative_counts

        # Cumulative sums for level_0
        for i in range(1, level_0_size):
            level_0[i] += level_0[i - 1]

        # Cumulative sums for level_1.  Two-step process:
        #
        # 1. Zero out the level_1 cumulative sums for the blocks that lie at
        # the beginning of an L0 upper block. (If we don't do that, the sums
        # could overflow.)
        for byte_offset in range(0, bit_array_byte_length, 1 << 29):
            level_1_idx = 2 * (byte_offset // 256)
            level_1[level_1_idx] = 0

        # 2. calculate the cumulative sums for level_1.
        byte_offset = 0
        for i in range(0, level_1_size, 2):
            if byte_offset % (1 << 29) != 0:
                level_1[i] += level_1[i - 2]
            byte_offset += 256

        return (level_0, level_1)

    def _initialize_select_structure(self) -> "List[array]":
        """
        For each upper block, we precompute the position of every 8192nd one bit
        (relative to the beginning of the upper block). These positions can be
        stored in 32 bits.
        """
        bit_array_byte_length = len(self._memory_view)
        select_structure: "List[array]" = []
        for level_0_idx, level_0_sum in enumerate(self._level_0):
            rank_start = level_0_sum

            rank_end = self.rank(
                min(
                    (level_0_idx + 1) * (1 << 32) - 1,
                    len(self._bit_array) - 1
                )
            )

            num_one_bits = rank_end - rank_start
            num_entries = math.ceil(num_one_bits / 8192)
            select_structure.append(array('L', [0] * num_entries))

            # Now scan through the upper level.
            popcount_sum = 0
            current_select_target = 0
            for byte_offset in range(
                (1 << 29) * level_0_idx,
                min(bit_array_byte_length, (1 << 29) * (level_0_idx + 1)),
                8
            ):
                old_sum = popcount_sum
                popcount_sum += popcount(self._memory_view[byte_offset:byte_offset + 8])
                if popcount_sum > current_select_target:
                    select_in_word = select(
                        self._memory_view[byte_offset:byte_offset + 8],
                        current_select_target - old_sum
                    )
                    select_structure[level_0_idx][(current_select_target) // 8192] = (
                        8 * (byte_offset - ((1 << 29) * level_0_idx)) + select_in_word
                    )
                    current_select_target += 8192

            for i in range(len(select_structure[level_0_idx])):
                assert select_structure[level_0_idx][i] >= 8192 * i
        return select_structure

    def _select(self, rank: int, sampling_answers: "Optional[List[array]]" = None) -> int:

        pass

    @staticmethod
    def _add_relative_count(
        *,
        basic_block_index: int,
        packed_relative_counts: int,
        pop_count: int
    ) -> int:
        # 1023 in binary is '1111111111', which is 10 one bits.
        shift_amount = 10 * basic_block_index
        old_count = (packed_relative_counts >> shift_amount) & 1023
        new_count = old_count + pop_count

        # The following bit twiddling is courtesy of "Bit Twiddling Hacks"
        # https://graphics.stanford.edu/~seander/bithacks.html#MaskedMerge

        # Value to merge in non-masked bits
        a = packed_relative_counts

        # Value to merge in masked bits
        b = new_count << shift_amount

        # 1 where bits from b should be selected; 0 where from a.
        mask = 1023 << shift_amount

        return a ^ ((a ^ b) & mask)

    @staticmethod
    def _get_relative_count(
        *,
        basic_block_index: int,
        packed_relative_counts: int
    ) -> int:
        # 1023 in binary is '1111111111', which is 10 one bits.
        shift_amount = 10 * basic_block_index
        return (packed_relative_counts >> shift_amount) & 1023

    def rank(self, i: int) -> int:
        """
        Returns the number of 1 bits up to and including position i.
        https://en.wikipedia.org/wiki/Succinct_data_structure#Succinct_dictionaries
        """
        byte_offset = i // 8

        sum_rank = 0
        level_0_idx = byte_offset // (1 << 29)
        sum_rank += self._level_0[level_0_idx]

        level_1_idx = (byte_offset // 256) * 2
        sum_rank += self._level_1[level_1_idx]

        basic_block_idx = (byte_offset % 256) // 64
        level_2_idx = level_1_idx + 1
        packed_relative_counts = self._level_1[level_2_idx]
        left_block_idx = 0
        while left_block_idx < basic_block_idx:
            sum_rank += self._get_relative_count(
                basic_block_index=left_block_idx,
                packed_relative_counts=packed_relative_counts
            )
            left_block_idx += 1

        # Now do a manual popcount within the current basic block.
        start_bit = 8 * (byte_offset // 64) * 64
        end_bit = i + 1

        while start_bit + 64 <= end_bit:
            start_byte = start_bit // 8
            sum_rank += popcount(
                self._memory_view[start_byte:(start_byte + 8)]
            )
            start_bit += 64

        while start_bit + 8 <= end_bit:
            start_byte = start_bit // 8
            sum_rank += RANK_IN_BYTE[256 * 7 + self._memory_view[start_byte]]
            start_bit += 8

        if start_bit < end_bit:
            slack = end_bit - start_bit - 1
            start_byte = start_bit // 8
            sum_rank += RANK_IN_BYTE[256 * slack + self._memory_view[start_byte]]

        return sum_rank

    def rank_zero(self, i: int) -> int:
        """
        Returns the number of 0 bits up to and including position i.
        """
        return i - self.rank(i) + 1

    def select(self, rank: int) -> int:
        """
        Returns the position of the 1-bit having the provided rank.
        If no such bit exists, -1 is returned.
        """

        # Use binary search to find the upper (L0) block that contains the
        # bit with the target rank.
        # level_0_idx = bisect.bisect_right(self._level_0, rank)
        level_0_idx = self._binary_search_level_0(rank)
        if level_0_idx < 0:
            level_0_idx = -(level_0_idx) - 1

        # Maintain an (absolute) bit range where the bit with the target rank
        # could be. This range if half open: [low, high)
        # low = (1<<32) * level_0_idx
        # high = min((1 << 32) * (level_0_idx + 1), len(self._bit_array))
        relative_rank = rank - self._level_0[level_0_idx]

        # Search the sampling answers corresponding to level_0_idx
        # Use them to find the lower block that contains the target
        # bit.
        sampling_answers = self._select_structure[level_0_idx]
        x = relative_rank // 8192
        if relative_rank % 8192 == 0:
            # Just use one of the precomputed answers.
            if x < len(sampling_answers):
                return sampling_answers[x]
            return -1

        # Otherwise we have to search.
        search_start_bit = sampling_answers[x]
        if x + 1 < len(sampling_answers):
            search_end_bit = sampling_answers[x + 1]
        else:
            search_end_bit = min(len(self._bit_array) - level_0_idx, (1 << 32) * (level_0_idx + 1))

        # Do a binary search for the L1 block that contains the 1-bit
        # with the desired relative rank.
        level_1_idx = self._binary_search_level_1(
            relative_rank,
            (search_start_bit // 2048) * 2,
            (search_end_bit // 2048) * 2 - 2
        )
        if level_1_idx < 0:
            level_1_idx = -(level_1_idx) - 2

        relative_rank -= self._level_1[level_1_idx]
        packed_relative_counts = self._level_1[level_1_idx + 1]

        for basic_block_idx in range(0, 4):
            if basic_block_idx == 3:
                break
            relative_count = self._get_relative_count(
                basic_block_index=basic_block_idx,
                packed_relative_counts=packed_relative_counts
            )
            if relative_rank < relative_count:
                break
            relative_rank -= relative_count

        # Now search within the 64-byte basic block.
        byte_offset = 64 * basic_block_idx + 256 * (level_1_idx // 2) + (1 << 29) * level_0_idx
        start_bit = 8 * (byte_offset // 64) * 64
        end_bit = min(
            start_bit + 2048,
            len(self._bit_array) - 1,
            (1 << 32) * (level_0_idx + 1) - 1
        )

        while start_bit + 64 <= end_bit:
            start_byte = start_bit // 8
            rank = popcount(
                self._memory_view[start_byte:(start_byte + 8)]
            )
            if relative_rank < rank:
                return start_bit + select(
                    self._memory_view[start_byte:(start_byte + 8)],
                    relative_rank
                )

            relative_rank -= rank
            start_bit += 64

        while start_bit + 8 <= end_bit:
            start_byte = start_bit // 8
            rank = RANK_IN_BYTE[256 * 7 + self._memory_view[start_byte]]
            if relative_rank < rank:
                return start_bit + SELECT_IN_BYTE[
                    256 * (relative_rank) + self._memory_view[start_byte]
                ]
            relative_rank -= rank
            start_bit += 8

        if start_bit < end_bit:
            slack = end_bit - start_bit - 1
            start_byte = start_bit // 8
            rank = RANK_IN_BYTE[256 * slack + self._memory_view[start_byte]]
            if relative_rank < rank:
                return start_bit + SELECT_IN_BYTE[
                    256 * (relative_rank) + self._memory_view[start_byte]
                ]
            relative_rank -= rank

        if relative_rank == 0 and self._bit_array[end_bit]:
            return end_bit

        return -1

    def _binary_search_level_0(self, x: int) -> int:
        low = 0
        high = len(self._level_0) - 1

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._level_0[mid]
            if mid_val < x:
                low = mid + 1
            elif mid_val > x:
                high = mid - 1
            else:
                return mid

        return -(high + 1)

    def _binary_search_level_1(self, x: int, from_idx: int, to_idx: int) -> int:
        low = from_idx // 2
        high = to_idx // 2

        while low <= high:
            mid = (low + high) >> 1
            mid_val = self._level_1[2 * mid]
            if mid_val < x:
                low = mid + 1
            elif mid_val > x:
                high = mid - 1
            else:
                return 2 * mid

        return -((high) + 1) * 2

    def __getitem__(self, key: int) -> bool:
        return self._bit_array[key]

    def __len__(self) -> int:
        return len(self._bit_array)

    def select_zero(self, rank_zero: int) -> int:
        low = 0
        high = len(self._bit_array) - 1

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
