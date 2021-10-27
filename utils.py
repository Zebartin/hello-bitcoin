import hashlib
import random
import string
import struct


def double_sha256(x: bytes) -> bytes:
    """两次SHA256哈希"""
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()


def ripemd160_sha256(x: bytes) -> bytes:
    """先SHA256后RIPEMD160"""
    return hashlib.new('ripemd160', hashlib.sha256(x).digest()).digest()


def int2hex(x: int, n: int) -> str:
    """将整数转成16进制字符串同时前置补0"""
    return '{0:0{1}x}'.format(x, n)


def ser_compact_size(x):
    """按照比特币的CompactSize Unsigned Integer编码序列化"""
    r = b''
    if x < 253:
        r = struct.pack('B', x)
    elif x < 0x10000:
        r = struct.pack('<BH', 253, x)
    elif x < 0x100000000:
        r = struct.pack('<BI', 254, x)
    else:
        r = struct.pack('<BQ', 255, x)
    return r


def deser_compact_size(f):
    """按照比特币的CompactSize Unsigned Integer编码反序列化"""
    nit = struct.unpack('<B', f.read(1))[0]
    if nit == 253:
        nit = struct.unpack('<H', f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack('<I', f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack('<Q', f.read(8))[0]
    return nit


def random_str(num: int = 16):
    """随机生成num长度的字符串"""
    while True:
        yield ''.join(random.sample(string.ascii_letters+string.digits+string.punctuation, num))
