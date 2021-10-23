import hashlib
import random
import string

def double_hash(x: bytes) -> bytes:
    """两次SHA256哈希"""
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()

def random_str(num: int = 16):
    """随机生成num长度的字符串"""
    while True:
        yield ''.join(random.sample(string.ascii_letters+string.digits+string.punctuation, num))