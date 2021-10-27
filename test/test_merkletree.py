import random
from merkletree import MerkleNode, MerkleTree
from utils import double_sha256, random_str


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
    return double_sha256(root.left.hash + root.right.hash) == root.hash \
        and verify_merklenode(root.left) and verify_merklenode(root.right)
