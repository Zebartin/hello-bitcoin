"""比特币账户，包含私钥、公钥和地址

使用样例：

a1 = Account.from_random_key(public_key_encoding='compressed')
a2 = Account.from_private_key('96a184d15a4e439af75d3ce8bfb55ac3cb9c48224ed90356fb5bbbb1d7aa13be')
m = b'hello bitcoin'
signature = a1.sign(m)
assert a1.verify(signature, m)
"""
from __future__ import annotations

import hashlib

import base58
from ecdsa import SECP256k1, SigningKey
from ecdsa.keys import BadSignatureError


class Account:
    """比特币账户

    属性：
        encoding: 公钥格式，压缩/非压缩
        signing_key: 公钥
        verifying_key: 私钥
        address: 账户地址，与公钥格式有关
        public_key: 公钥的字符串形式
        private_key: 私钥的字符串形式
    """

    def __init__(self, signing_key, public_key_encoding) -> None:
        self.encoding = public_key_encoding
        self.signing_key = signing_key
        self.verifying_key = self.signing_key.verifying_key
        # base58库提供的base58check编码没有添加version前缀，需自行添加0x00
        self.address = base58.b58encode_check(b'\x00'+hashlib.new('ripemd160', hashlib.sha256(
            self.verifying_key.to_string(encoding=public_key_encoding)).digest()).digest()).decode()

    @classmethod
    def from_private_key(cls, private_key: str | bytes, public_key_encoding='uncompressed') -> Account:
        """由给定的私钥创建账户"""
        if isinstance(private_key, str):
            private_key = bytes.fromhex(private_key)
        elif not isinstance(private_key, bytes):
            raise TypeError('私钥类型应为bytes或16进制字符串')
        signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
        return cls(signing_key, public_key_encoding)

    @classmethod
    def from_random_key(cls, public_key_encoding='uncompressed') -> Account:
        """创建随机账户"""
        signing_key = SigningKey.generate(SECP256k1)
        return cls(signing_key, public_key_encoding)

    @property
    def public_key(self) -> str:
        return self.verifying_key.to_string(encoding=self.encoding).hex()

    @property
    def private_key(self) -> str:
        return self.signing_key.to_string().hex()

    def sign(self, msg: bytes) -> bytes:
        return self.signing_key.sign(msg)

    def verify(self, sig, msg: bytes) -> bool:
        try:
            return self.verifying_key.verify(sig, msg)
        except BadSignatureError:
            return False
