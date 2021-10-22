from __future__ import annotations
from collections.abc import Iterable
import logging

from utils import double_hash


class MerkleNode:
    def __init__(self, data: str) -> None:
        if not isinstance(data, str):
            raise TypeError('Merkle树节点数据应为str类型')
        self.hash = double_hash(data)
        self.left: MerkleNode = None
        self.right: MerkleNode = None

    @staticmethod
    def parent(left: MerkleNode, right: MerkleNode) -> MerkleNode:
        parent_node = MerkleNode(left.hash + right.hash)
        parent_node.left = left
        parent_node.right = right
        return parent_node

    def __str__(self):
        return self.hash[:4]


class MerkleTree:
    def __init__(self, data) -> None:
        if not isinstance(data, Iterable):
            raise TypeError('Merkle树的data应为可迭代对象')
        layer_nodes = [MerkleNode(x) for x in data]
        while len(layer_nodes) > 1:
            if len(layer_nodes) % 2:
                layer_nodes.append(layer_nodes[-1])
            assert(len(layer_nodes) % 2 == 0)

            for i in range(len(layer_nodes) // 2):
                layer_nodes[i] = MerkleNode.parent(
                    layer_nodes[i * 2], layer_nodes[i * 2 + 1])
            layer_nodes = layer_nodes[:len(layer_nodes) // 2]

            logging.debug('当前Merkle节点：')
            logging.debug('\t'.join([str(n) for n in layer_nodes]))
        self.root = layer_nodes[0]

    @staticmethod
    def make_merkle_tree(data) -> MerkleTree:
        return MerkleTree(data)
