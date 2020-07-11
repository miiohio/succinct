from dataclasses import dataclass
from succinct.louds import LoudsBinaryTree
from typing import Dict, Optional


def test_louds_binary_tree() -> None:
    """
    Basic example from Chapter 8.1 of "Compact Data Structures"
    """
    @dataclass
    class TreeNode:
        id: int
        parent: "Optional[TreeNode]" = None
        left_child: "Optional[TreeNode]" = None
        right_child: "Optional[TreeNode]" = None

    tree_nodes: Dict[int, TreeNode] = {
        i: TreeNode(id=i) for i in range(0, 12)
    }

    tree_nodes[0].left_child = tree_nodes[1]
    tree_nodes[0].right_child = tree_nodes[2]

    tree_nodes[1].left_child = tree_nodes[3]
    tree_nodes[1].right_child = tree_nodes[4]

    tree_nodes[2].right_child = tree_nodes[5]

    tree_nodes[4].left_child = tree_nodes[6]
    tree_nodes[4].right_child = tree_nodes[7]

    tree_nodes[5].left_child = tree_nodes[8]

    tree_nodes[6].right_child = tree_nodes[9]

    tree_nodes[8].left_child = tree_nodes[10]
    tree_nodes[8].right_child = tree_nodes[11]

    louds = LoudsBinaryTree(
        root=tree_nodes[0],
        get_left_child=lambda n: n.left_child,
        get_right_child=lambda n: n.right_child
    )

    for n in tree_nodes.values():
        for child in [n.left_child, n.right_child]:
            if child is not None:
                assert louds.get_parent(child.id) == n.id

        assert louds.get_left_child(n.id) == (n.left_child.id if n.left_child is not None else None)
        assert louds.get_right_child(n.id) == (n.right_child.id if n.right_child is not None else None)

        if n.left_child is None and n.right_child is None:
            assert louds.is_leaf(n.id)
