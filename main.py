import json
import os
import random

import click

from account import Account
from block import Block, BlockHeader
from transaction import Transaction


@click.command()
@click.option('-a', '--account', default=100, help='生成账户的数量')
@click.option('-t', '--transaction', default=1000, help='生成交易的数量')
@click.option('-b', '--block', default=10, help='生成区块的数量')
@click.option('-o', '--output', type=click.Path(), default=os.getcwd(), help='结果输出路径')
def cli(account, transaction, block, output):
    # 随机生成account个随机公钥编码格式的Account
    public_key_encoding = ('compressed', 'uncompressed')
    accounts = [Account.from_random_key(
        public_key_encoding[random.randint(0, 1)]) for _ in range(account)]
    # 根据上面生成的账户随机生成transaction个Transaction
    txs = []
    for _ in range(transaction):
        # 输入输出数量随机
        n_vin = random.randint(1, 10)
        n_vout = random.randint(1, 10)
        account_picked = random.sample(accounts, n_vin+n_vout)
        txs.append(Transaction.generate(
            account_in=account_picked[:n_vin],
            account_out=account_picked[n_vin:]
        ))
    # 将上述交易平均分配到随机生成的block个区块
    tx_per_block = transaction // block
    prev_hash = 0
    blocks = []
    for i in range(0, transaction, tx_per_block):
        bhdr = BlockHeader(
            version=1,
            prev_block_hash=prev_hash,
            merkle_root=None,
            timestamp=0,
            target=0,
            nonce=0
        )
        blocks.append(Block(bhdr, txs[i:i+tx_per_block]))
        prev_hash = blocks[-1].header.hash
    # 将生成结果以json格式输出到文件中
    with open(os.path.join(output, 'blocks.json'), 'w', encoding='utf-8') as f:
        json.dump({b.header.hash: b.to_dict() for b in blocks}, f, indent=4)
    with open(os.path.join(output, 'accounts.json'), 'w', encoding='utf-8') as f:
        json.dump({a.address: {
            'private key': a.private_key,
            'public key': a.public_key
        } for a in accounts}, f, indent=4)
