import math
from collections import deque
from typing import Callable, Optional, TypeVar

from succinct.poppy import Poppy

from bitarray import bitarray

A = TypeVar('A')


class LoudsBinaryTree:
    def __init__(
        self,
        *,
        root: A,
        get_left_child: Callable[[A], Optional[A]],
        get_right_child: Callable[[A], Optional[A]]
    ) -> None:
        queue = deque([root])

        self._bits = bitarray()
        while queue:
            tree_node = queue.popleft()
            for child in [get_left_child(tree_node), get_right_child(tree_node)]:
                if child is not None:
                    self._bits.append(True)
                    queue.append(child)
                else:
                    self._bits.append(False)
        self._poppy = Poppy(self._bits)

    def get_root(self) -> int:
        return 0

    def get_parent(self, i: int) -> Optional[int]:
        if i == 0:
            return None
        return math.floor(self._poppy.select(i - 1) / 2)

    def get_left_child(self, i: int) -> Optional[int]:
        if not self._bits[2 * i]:
            return None
        return self._poppy.rank(2 * i)

    def get_right_child(self, i: int) -> Optional[int]:
        if not self._bits[2 * i + 1]:
            return None
        return self._poppy.rank(2 * i + 1)

    def is_leaf(self, i: int) -> bool:
        return not (self._bits[2 * i] or self._bits[2 * i + 1])
