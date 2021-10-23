import random
import pytest
from merkletree import MerkleNode, MerkleTree
from utils import random_str


def test_double_hash():
    assert MerkleNode.double_hash(b'hello bitcoin').hex() \
        == '858f460a0abb5bff621b7e625416ba9e2239e36c06ecb469088b6eff9bed5103'


def test_merkletree():
    rs = random_str()
    mock_txs = [next(rs) for _ in range(random.randint(1, 129))]
    tree = MerkleTree.make_merkle_tree(mock_txs)
    assert verify_merklenode(tree.root)


def verify_merklenode(root: MerkleNode) -> bool:
    if root.left is None or root.right is None:
        if root.left is None and root.right is None:
            return True
        return False
    return MerkleNode.double_hash(root.left.hash + root.right.hash) == root.hash \
        and verify_merklenode(root.left) and verify_merklenode(root.right)
