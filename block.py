"""比特币区块

使用样例：

header = BlockHeader(0, 0, 0, 0, 0, 0)
block = Block(header, [...])
block.serialize()
print(block.headr.hash)
print(block.to_dict())
"""
from __future__ import annotations

import struct
from typing import Dict, List

from merkletree import MerkleTree
from transaction import Transaction
from utils import deser_compact_size, double_sha256, int2hex, ser_compact_size


class BlockHeader:
    """区块头部

    属性：
        version
        prev_block_hash
        merkle_root
        timestamp
        target
        nonce
        hash: 区块头部哈希值
    """

    def __init__(self, version: int, prev_block_hash: int | str, merkle_root: int, timestamp: int, target: int, nonce: int) -> None:
        self.version = version
        if isinstance(prev_block_hash, str):
            prev_block_hash = int(prev_block_hash, 16)
        self.prev_block_hash = prev_block_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.target = target
        self.nonce = nonce

    def serialize(self) -> bytes:
        ret = b""
        ret += struct.pack("<i", self.version)
        tmp = self.prev_block_hash
        # 小端存放
        for _ in range(8):
            ret += struct.pack("<I", tmp & 0xFFFFFFFF)
            tmp >>= 32
        tmp = self.merkle_root
        # 小端存放
        for _ in range(8):
            ret += struct.pack("<I", tmp & 0xFFFFFFFF)
            tmp >>= 32
        ret += struct.pack("<I", self.timestamp)
        ret += struct.pack("<I", self.target)
        ret += struct.pack("<I", self.nonce)
        return ret

    @classmethod
    def deserialize(cls, f) -> BlockHeader:
        version = struct.unpack("<i", f.read(4))[0]
        prev_block_hash = 0
        for i in range(8):
            t = struct.unpack("<I", f.read(4))[0]
            prev_block_hash += t << (i * 32)
        merkle_root = 0
        for i in range(8):
            t = struct.unpack("<I", f.read(4))[0]
            merkle_root += t << (i * 32)
        timestamp = struct.unpack("<I", f.read(4))[0]
        target = struct.unpack("<I", f.read(4))[0]
        nonce = struct.unpack("<I", f.read(4))[0]
        return cls(version, prev_block_hash, merkle_root, timestamp, target, nonce)

    @property
    def hash(self) -> str:
        return double_sha256(self.serialize())[::-1].hex()

    def to_dict(self) -> Dict:
        return {
            'version': self.version,
            'hash': self.hash,
            'previous block hash': int2hex(self.prev_block_hash, 64),
            'merkle root': int2hex(self.merkle_root, 64),
            'target': self.target,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
        }


class Block:
    """区块

    属性：
        header
        txs: 区块包含的所有交易
    """

    def __init__(self, header: BlockHeader, txs: List[Transaction]) -> None:
        self.header = header
        self.txs = txs
        if not self.header.merkle_root:
            self.header.merkle_root = self.__cal_merkle_root()

    def __cal_merkle_root(self) -> int:
        return int.from_bytes(MerkleTree.make_merkle_tree([tx.serialize() for tx in self.txs]).root.hash, 'little')

    def serialize(self) -> bytes:
        ret = b''
        ret += self.header.serialize()
        ret += ser_compact_size(len(self.txs))
        for i in self.txs:
            ret += i.serialize()
        return ret

    @classmethod
    def deserialize(cls, f) -> Block:
        bh = BlockHeader.deserialize(f)
        n_txs = deser_compact_size(f)
        txs = []
        for _ in range(n_txs):
            txs.append(Transaction.deserialize(f))
        return cls(bh, txs)

    def is_valid(self) -> bool:
        return self.__cal_merkle_root() == self.header.merkle_root

    def to_dict(self) -> Dict:
        return {
            **self.header.to_dict(),
            'tx': [tx.to_dict() for tx in self.txs]
        }
