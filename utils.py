import random
import string


def random_str(num: int = 16):
    """随机生成num长度的字符串"""
    while True:
        yield ''.join(random.sample(string.ascii_letters+string.digits+string.punctuation, num))
