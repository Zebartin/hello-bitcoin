"""比特币交易

使用样例：

ain = [Account.from_random_key() for _ in range(3)]
aout = [Account.from_random_key() for _ in range(2)]
tx = Transaction.generate(ain, aout)
print(tx.serialize().hex())
print(tx)
"""
from __future__ import annotations

import random
import struct
from typing import Dict, List

from base58 import b58decode_check

from account import Account
from utils import deser_compact_size, double_sha256, int2hex, random_str, ser_compact_size


def make_P2PKH_scriptPubKey(pubkey_hash: bytes) -> bytes:
    """生成公钥对应的P2PKH脚本"""
    OP_DUP = b'\x76'
    OP_HASH160 = b'\xa9'
    OP_EQUALVERIFY = b'\x88'
    OP_CHECKSIG = b'\xac'
    return OP_DUP + OP_HASH160 + struct.pack('B', len(pubkey_hash)) + pubkey_hash + OP_EQUALVERIFY + OP_CHECKSIG


def make_scriptSig(sig: bytes, pubkey: str, sighash=b'\x01') -> bytes:
    """生成签名和公钥对应的脚本"""
    pubkey_bytes = bytes.fromhex(pubkey)
    return struct.pack('B', len(sig) + 1) + sig + sighash + struct.pack('B', len(pubkey_bytes)) + pubkey_bytes


class TxIn:
    """交易输入

    属性：
        txid: UTXO交易id
        vout: UTOX输出index
        scriptSig: bytes类型的脚本
        sequence
    """

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
        ret += ser_compact_size(len(self.scriptSig))
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
        scirptSig_len = deser_compact_size(f)
        scriptSig = f.read(scirptSig_len)
        sequence = struct.unpack("<I", f.read(4))[0]
        return cls(txid, vout, scriptSig, sequence)

    def to_dict(self) -> Dict:
        return {
            'txid': int2hex(self.txid, 64),
            'vout': self.vout,
            'scriptSig': self.scriptSig.hex(),
            'sequence': int2hex(self.sequence, 8)
        }


class TxOut:
    """交易输出

    属性：
        value: 交易额，以聪（satoshi）为单位
        scriptPubKey: bytes类型的脚本
    """

    def __init__(self, value: int, scriptPubKey: bytes) -> None:
        self.value = value
        self.scriptPubKey = scriptPubKey

    def serialize(self) -> bytes:
        ret = b''
        ret += struct.pack('<Q', self.value)
        ret += ser_compact_size(len(self.scriptPubKey))
        ret += self.scriptPubKey
        return ret

    @classmethod
    def deserialize(cls, f) -> TxOut:
        value = struct.unpack("<Q", f.read(8))[0]
        scriptPubKey_len = deser_compact_size(f)
        scriptPubKey = f.read(scriptPubKey_len)
        return cls(value, scriptPubKey)

    def to_dict(self) -> Dict:
        return {
            'value': f'{self.value // 100000000}.{self.value % 100000000:08}',
            'scriptPubKey': self.scriptPubKey.hex()
        }


class Transaction:
    """交易

    属性：
        version: 版本号
        vin: 输入
        vout: 输出
        locktime
        txid: 交易ID
    """

    def __init__(self, version: int, vin: List[TxIn], vout: List[TxOut], locktime: int) -> None:
        self.version = version
        self.vin = vin
        self.vout = vout
        self.locktime = locktime

    def serialize(self) -> bytes:
        ret = b''
        ret += struct.pack("<i", self.version)
        ret += ser_compact_size(len(self.vin))
        for i in self.vin:
            ret += i.serialize()
        ret += ser_compact_size(len(self.vout))
        for i in self.vout:
            ret += i.serialize()
        ret += struct.pack("<I", self.locktime)
        return ret

    @classmethod
    def deserialize(cls, f) -> Transaction:
        version = struct.unpack("<i", f.read(4))[0]
        vin_size = deser_compact_size(f)
        vin = []
        for _ in range(vin_size):
            vin.append(TxIn.deserialize(f))
        vout_size = deser_compact_size(f)
        vout = []
        for _ in range(vout_size):
            vout.append(TxOut.deserialize(f))
        locktime = struct.unpack("<I", f.read(4))[0]
        return cls(version, vin, vout, locktime)

    @property
    def txid(self) -> str:
        return double_sha256(self.serialize())[::-1].hex()

    def to_dict(self) -> Dict:
        return {
            'hash': self.txid,
            'version': self.version,
            'vin': [i.to_dict() for i in self.vin],
            'vout': [i.to_dict() for i in self.vout],
            'locktime': self.locktime
        }

    @classmethod
    def generate(cls, account_in: List[Account], accout_out: List[Account]) -> Transaction:
        """随机生成一笔交易，输入输出的地址或者签名由参数中的Account指定"""
        N_8F = (1 << 32) - 1
        rs = random_str()
        n_vin = len(account_in)
        n_vout = len(accout_out)
        vin = []
        vout = []
        for i in range(n_vin):
            # 随机输入：
            #   用随机字符串伪造交易id
            #   随机4bytes的vout
            #   空的脚本
            #   全F的sequence
            txid = int.from_bytes(double_sha256(next(rs).encode()), 'big')
            _vout = random.randint(0, N_8F)
            vin.append(TxIn(txid, _vout, b'', N_8F))
        for i in range(n_vout):
            # 随机输出：
            #   随机交易额，限制在相对合理的范围内
            #   对应账户生成的pubkey脚本
            value = random.randint(1, N_8F)
            pubkey_hash = b58decode_check(accout_out[i].address)
            scriptPubKey = make_P2PKH_scriptPubKey(pubkey_hash)
            vout.append(TxOut(value, scriptPubKey))

        tx = cls(1, vin, vout, 0)
        tx_msg = tx.serialize()
        # 补上各个输入对不含sig脚本的交易的签名
        for i in range(n_vin):
            sig = account_in[i].sign(tx_msg)
            tx.vin[i].scriptSig = make_scriptSig(sig, account_in[i].public_key)
        return tx
