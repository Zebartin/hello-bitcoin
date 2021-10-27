import hashlib
import random
import string


def double_sha256(x: bytes) -> bytes:
    """两次SHA256哈希"""
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()


def ripemd160_sha256(x: bytes) -> bytes:
    """先SHA256后RIPEMD160"""
    return hashlib.new('ripemd160', hashlib.sha256(x).digest()).digest()


def int2hex(x: int, n: int) -> str:
    """将整数转成16进制字符串同时前置补0"""
    return '{0:0{1}x}'.format(x, n)


def random_str(num: int = 16):
    """随机生成num长度的字符串"""
    while True:
        yield ''.join(random.sample(string.ascii_letters+string.digits+string.punctuation, num))
