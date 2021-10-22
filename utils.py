import hashlib
import random
import string

def double_hash(x: str) -> str:
    return hashlib.sha256(hashlib.sha256(x.encode()).hexdigest().encode()).hexdigest()

def random_str(num: int = 16):
    while True:
        yield ''.join(random.sample(string.ascii_letters+string.digits+string.punctuation, num))