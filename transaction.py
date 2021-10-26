from __future__ import annotations
from typing import Dict, List
import json
import struct


def make_P2PKH_scriptPubKey(pubkey: str) -> bytes:
    """生成公钥对应的P2PKH脚本"""
    OP_DUP = b'\x76'
    OP_HASH160 = b'\xa9'
    OP_EQUALVERIFY = b'\x88'
    OP_CHECKSIG = b'\xac'
    pubkey_bytes = bytes.fromhex(pubkey)
    return OP_DUP + OP_HASH160 + struct.pack('B', len(pubkey_bytes)) + pubkey_bytes + OP_EQUALVERIFY + OP_CHECKSIG


def make_scriptSig(sig: bytes, pubkey: str, sighash=b'\x01') -> bytes:
    """生成签名和公钥对应的脚本"""
    pubkey_bytes = bytes.fromhex(pubkey)
    return struct.pack('B', len(sig) + 1) + sig + sighash + struct.pack('B', len(pubkey_bytes)) + pubkey_bytes


class TxIn:
    def __init__(self, txid: int, vout: int, scriptSig: bytes, sequence: int) -> None:
        self.txid = txid
        self.vout = vout
        self.scriptSig = scriptSig
        self.sequence = sequence

    def serialize(self) -> bytes:
        ret = b''
        tmp = self.txid
        # 小端存放
        for _ in range(8):
            ret += struct.pack("<I", tmp & 0xFFFFFFFF)
            tmp >>= 32
        ret += struct.pack('<I', self.vout)
        # 这里本来应该按比特币的CompactSize Unsigned Integer编码
        # scriptSig长度不会大于140bytes，可以简单处理，下同
        ret += struct.pack('B', len(self.scriptSig))
        ret += self.scriptSig
        ret += struct.pack('<I', self.sequence)
        return ret

    @classmethod
    def deserialize(cls, f) -> TxIn:
        txid = 0
        for i in range(8):
            t = struct.unpack("<I", f.read(4))[0]
            txid += t << (i * 32)
        vout = struct.unpack("<I", f.read(4))[0]
        scirptSig_len = struct.unpack("<B", f.read(1))[0]
        scriptSig = f.read(scirptSig_len)
        sequence = struct.unpack("<I", f.read(4))[0]
        return cls(txid, vout, scriptSig, sequence)

    def to_dict(self) -> Dict:
        return {
            'txid': hex(self.txid)[2:],
            'vout': self.vout,
            'scriptSig': self.scriptSig.hex(),
            'sequence': hex(self.sequence)[2:]
        }


class TxOut:
    def __init__(self, value: int, scriptPubKey: bytes) -> None:
        self.value = value
        self.scriptPubKey = scriptPubKey

    def serialize(self) -> bytes:
        ret = b''
        ret += struct.pack('<q', self.value)
        ret += struct.pack('B', len(self.scriptPubKey))
        ret += self.scriptPubKey
        return ret

    @classmethod
    def deserialize(cls, f) -> TxOut:
        value = struct.unpack("<q", f.read(8))[0]
        scriptPubKey_len = struct.unpack("<B", f.read(1))[0]
        scriptPubKey = f.read(scriptPubKey_len)
        return cls(value, scriptPubKey)

    def to_dict(self) -> Dict:
        return {
            'value': f'{self.value // 100000000}.{self.value % 100000000:08}',
            'scriptPubKey': self.scriptPubKey.hex()
        }


class Transaction:
    def __init__(self, version: int, vin: List[TxIn], vout: List[TxOut], locktime: int) -> None:
        self.version = version
        self.vin = vin
        self.vout = vout
        self.locktime = locktime

    def serialize(self) -> bytes:
        ret = b''
        ret += struct.pack("<i", self.version)
        ret += struct.pack("B", len(self.vin))
        for i in self.vin:
            ret += i.serialize()
        ret += struct.pack("B", len(self.vout))
        for i in self.vout:
            ret += i.serialize()
        ret += struct.pack("<I", self.locktime)
        return ret

    @classmethod
    def deserialize(cls, f) -> Transaction:
        version = struct.unpack("<i", f.read(4))[0]
        vin_size = struct.unpack("<B", f.read(1))[0]
        vin = []
        for _ in range(vin_size):
            vin.append(TxIn.deserialize(f))
        vout_size = struct.unpack("<B", f.read(1))[0]
        vout = []
        for _ in range(vout_size):
            vout.append(TxOut.deserialize(f))
        locktime = struct.unpack("<I", f.read(4))[0]
        return cls(version, vin, vout, locktime)

    def to_dict(self) -> Dict:
        return {
            'version': self.version,
            'vin': [i.to_dict() for i in self.vin],
            'vout': [i.to_dict() for i in self.vout],
            'locktime': self.locktime
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
