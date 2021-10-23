"""Merkle Tree在比特币系统中的简单实现

使用样例：

merkle_tree = MerkleTree.make_merkle_tree(['big', 'brother', 'is', 'watching', 'you'])
"""
from __future__ import annotations
from collections.abc import Iterable
import logging
import hashlib


class MerkleNode:
    """Merkle树的节点

    属性：
        hash: 节点的hash值
        left: 左子节点
        right: 右子节点
    """

    def __init__(self, data: str | bytes) -> None:
        if isinstance(data, str):
            data = data.encode()
        if not isinstance(data, bytes):
            raise TypeError('Merkle树节点数据应为bytes或str类型')
        self.hash: bytes = MerkleNode.double_hash(data)
        self.left: MerkleNode = None
        self.right: MerkleNode = None

    @staticmethod
    def parent(left: MerkleNode, right: MerkleNode) -> MerkleNode:
        """由两个节点计算得到它们的父节点"""
        parent_node = MerkleNode(left.hash + right.hash)
        parent_node.left = left
        parent_node.right = right
        return parent_node

    @staticmethod
    def double_hash(x: bytes) -> bytes:
        """两次SHA256哈希"""
        return hashlib.sha256(hashlib.sha256(x).digest()).digest()

    def __str__(self):
        return self.hash.hex()[:8]


class MerkleTree:
    """Merkle树

    属性：
        root: 根节点
    """

    def __init__(self, data) -> None:
        if not isinstance(data, Iterable):
            raise TypeError('Merkle树的data应为可迭代对象')
        layer_nodes = [MerkleNode(x) for x in data]
        if len(layer_nodes) == 0:
            return None
        # 自底向上构建merkle树
        while len(layer_nodes) > 1:
            # 如果是奇数个节点，重复最后一个节点
            if len(layer_nodes) % 2:
                layer_nodes.append(layer_nodes[-1])
            assert len(layer_nodes) % 2 == 0

            # 在layer_nodes中原地生成每层的节点
            for i in range(len(layer_nodes) // 2):
                layer_nodes[i] = MerkleNode.parent(
                    layer_nodes[i * 2], layer_nodes[i * 2 + 1])
            layer_nodes = layer_nodes[:len(layer_nodes) // 2]

            logging.debug('当前Merkle节点：')
            logging.debug('\t'.join([str(n) for n in layer_nodes]))
        self.root = layer_nodes[0]

    @staticmethod
    def make_merkle_tree(data) -> MerkleTree:
        """生成merkle树"""
        return MerkleTree(data)
