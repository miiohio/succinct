import heapq
from abc import ABCMeta, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Iterator, List
from typing_extensions import Protocol

from bitarray import bitarray
from succinct.louds import LoudsBinaryTree
from succinct.poppy import Poppy


class IndexedIntSequence(Protocol):
    def __getitem__(self, key: int) -> int:
        pass

    def __len__(self) -> int:
        pass


class HuffmanTreeNode(metaclass=ABCMeta):
    @abstractmethod
    def __len__(self) -> int:
        pass

    def __lt__(self, other: "HuffmanTreeNode") -> bool:
        return len(self) < len(other)

    @abstractmethod
    def iterator(
        self,
        values: IndexedIntSequence,
        merge_sort_bitarray: bitarray
    ) -> Iterator[int]:
        pass


@dataclass
class HuffmanInnerNode(HuffmanTreeNode):
    size: int
    left_child: HuffmanTreeNode
    right_child: HuffmanTreeNode
    merge_sort_offset: int

    def __len__(self) -> int:
        return self.size

    def iterator(
        self,
        values: IndexedIntSequence,
        merge_sort_bitarray: bitarray
    ) -> Iterator[int]:
        it_left = self.left_child.iterator(values, merge_sort_bitarray)
        it_right = self.right_child.iterator(values, merge_sort_bitarray)

        for b in merge_sort_bitarray[self.merge_sort_offset:(self.merge_sort_offset + self.size)]:
            if not b:
                yield next(it_left)
            else:
                yield next(it_right)


@dataclass(frozen=True)
class Run(HuffmanTreeNode):
    from_: int
    until: int

    def __len__(self) -> int:
        return self.until - self.from_

    def iterator(
        self,
        values: IndexedIntSequence,
        merge_sort_bitarray: bitarray
    ) -> Iterator[int]:
        yield from (values[i] for i in range(self.from_, self.until))


class Permutation:
    def __init__(self, values: IndexedIntSequence) -> None:
        runs = self._extract_runs(values)
        self._build_huffman_tree(values, runs)

    def _extract_runs(self, values: IndexedIntSequence) -> List[HuffmanTreeNode]:
        run_starts: List[int] = [0]

        for i in range(1, len(values)):
            if values[i] < values[i - 1]:
                run_starts.append(i)

        run_starts_bitarray = bitarray(len(values))
        run_starts_bitarray.setall(False)
        for start in run_starts:
            run_starts_bitarray[start] = True
        self._run_starts = Poppy(run_starts_bitarray)

        runs: List[HuffmanTreeNode] = []
        for i in range(len(run_starts)):
            from_index = run_starts[i]
            until_index = run_starts[i + 1] if i + 1 < len(run_starts) else len(values)
            runs.append(Run(from_=from_index, until=until_index))

        return runs

    def _build_huffman_tree(self, values: IndexedIntSequence, tree_nodes: List[HuffmanTreeNode]) -> None:
        # Determine the tree topology.
        heapq.heapify(tree_nodes)
        merge_sort_bitarray = bitarray()
        merge_sort_offset = 0
        while len(tree_nodes) > 1:
            x = heapq.heappop(tree_nodes)
            y = heapq.heappop(tree_nodes)
            merged = HuffmanInnerNode(
                size=len(x) + len(y),
                left_child=x,
                right_child=y,
                merge_sort_offset=merge_sort_offset
            )

            # Populate the merge sort bitarray's values
            it_left = ((value, False) for value in x.iterator(values, merge_sort_bitarray))
            it_right = ((value, True) for value in y.iterator(values, merge_sort_bitarray))

            for _, b in heapq.merge(it_left, it_right):
                merge_sort_bitarray.append(b)
                merge_sort_offset += 1

            heapq.heappush(tree_nodes, merged)

        # Build a LOUDS representation of the tree topology
        louds = LoudsBinaryTree(
            root=tree_nodes[0],
            get_left_child=lambda n: n.left_child if isinstance(n, HuffmanInnerNode) else None,
            get_right_child=lambda n: n.right_child if isinstance(n, HuffmanInnerNode) else None
        )

        # The data stored at each node of the tree is:
        # - The offset into a bitarray (if a node is an inner node)
        # - The offset into the original permutation (if a node is a leaf node)
        node_data: List[int] = []
        sizes: List[int] = []
        queue = deque(tree_nodes)
        while queue:
            tree_node = queue.popleft()
            if isinstance(tree_node, HuffmanInnerNode):
                node_data.append(tree_node.merge_sort_offset)
                sizes.append(len(tree_node))
                queue.append(tree_node.left_child)
                queue.append(tree_node.right_child)
            elif isinstance(tree_node, Run):
                node_data.append(tree_node.from_)
                sizes.append(len(tree_node))
            else:
                raise TypeError

        self._louds = louds
        self._node_data = node_data
        self._merge_sort_poppy = Poppy(merge_sort_bitarray)

        number_of_runs = self._run_starts.rank(len(self._run_starts) - 1)
        self._run_rank_to_louds_id = [0] * number_of_runs
        for louds_id in range(len(self._node_data)):
            if self._louds.is_leaf(louds_id):
                run_offset = self._node_data[louds_id]
                run_rank = self._run_starts.rank(run_offset)
                self._run_rank_to_louds_id[run_rank - 1] = louds_id

    def __getitem__(self, key: int) -> int:
        """
        Retrieve the i'th element of this permutation.
        """

        """
        Start at the leaves. Find the index of the current key `k` in the current
        node. Now, consider the parent node:
            - If the current node is the left child, get the index of the `k`'th
              zero in the parent node via "select_zero".

            - If the current node is the right child, get the index of the `k`th
            one in the parent node via "select".

        Repeat until the current node is the root, and return `k`.
        """
        run_start = self._run_starts.rank(key) - 1
        current_node = self._run_rank_to_louds_id[run_start]
        key = key - self._node_data[current_node]

        while True:
            parent = self._louds.get_parent(current_node)
            if parent is None:
                return key
            else:
                parent_offset = self._node_data[parent]
                if self._louds.get_left_child(parent) == current_node:
                    # # get the index of the `k`'th zero in the parent node
                    parent_rank_zero = (
                        0 if parent_offset == 0 else
                        self._merge_sort_poppy.rank_zero(parent_offset - 1)
                    )
                    key = self._merge_sort_poppy.select_zero(key + parent_rank_zero) - parent_offset
                    current_node = parent
                else:
                    # get the index of the `k`th one in the parent node
                    parent_rank = (
                        0 if parent_offset == 0 else
                        self._merge_sort_poppy.rank(parent_offset - 1)
                    )
                    key = self._merge_sort_poppy.select(key + parent_rank) - parent_offset
                    current_node = parent

    def index_of(self, value: int) -> int:
        """
        Retrieve the index of the given value within this permutation. (This is
        the inverse of the permutation.)
        """

        """
        Start at the root.  Look up the bit at position `value`. Calculate either
        the rank_1 or rank_0 of that position, depending on whether it's 1 or 0.
        Recurse to either the left or right child, depending on that value.
        """
        current_node = self._louds.get_root()
        while True:
            if self._louds.is_leaf(current_node):
                return self._node_data[current_node] + value
            else:
                offset = self._node_data[current_node]
                bit_value = self._merge_sort_poppy[offset + value]

                if not bit_value:
                    value = (
                        self._merge_sort_poppy.rank_zero(offset + value) -
                        (
                            0 if offset == 0 else
                            self._merge_sort_poppy.rank_zero(offset - 1)
                        )
                    ) - 1
                    child = self._louds.get_left_child(current_node)
                else:
                    value = (
                        self._merge_sort_poppy.rank(offset + value) -
                        (
                            0 if offset == 0 else
                            self._merge_sort_poppy.rank(offset - 1)
                        )
                    ) - 1
                    child = self._louds.get_right_child(current_node)
                assert child is not None
                current_node = child
