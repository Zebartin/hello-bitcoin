import random
from io import BytesIO

import pytest
import requests

from block import Block


def get_raw_block(block_height):
    """利用[Blockchain Data API](https://blockchain.info/api/blockchain_api)获取真实区块信息"""
    session = requests.Session()
    root_url = 'https://blockchain.info/'
    r = session.get(
        f'{root_url}/block-height/{block_height}?format=json').json()
    # 取同一高度的第一个区块
    block_hash = r['blocks'][0]['hash']
    block_json = session.get(
        f'{root_url}/rawblock/{block_hash}').json()
    block_hex = session.get(
        f'{root_url}/rawblock/{block_hash}?format=hex').text
    return block_json, Block.deserialize(BytesIO(bytes.fromhex(block_hex)))


@pytest.fixture
def random_real_block():
    # 保守地取高度在200000以内的区块
    return get_raw_block(random.randint(0, 200000))


def test_block(random_real_block):
    block_json, block = random_real_block
    assert block.header.hash == block_json['hash']
    assert len(block_json['tx']) == len(block.txs)
    assert block.is_valid()
    for a, b in zip(block_json['tx'], block.txs):
        assert a['hash'] == b.txid
