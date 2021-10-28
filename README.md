# hello-bitcoin
区块链课程作业
## 实验环境

- 操作系统：Windows 10 WSL2 + Ubuntu 20.04
- Python版本：3.9.6

```
$ git clone https://github.com/Zebartin/hello-bitcoin.git
```

配置好Python虚拟环境后，运行以下命令安装脚本：

```
$ pip install --editable .
```

安装完成后运行脚本：

```
$ hello-bitcoin --help
Usage: hello-bitcoin [OPTIONS]

Options:
  -a, --account INTEGER      生成账户的数量  [default: 100]
  -t, --transaction INTEGER  生成交易的数量  [default: 1000]
  -b, --block INTEGER        生成区块的数量  [default: 10]
  -o, --output PATH          结果输出路径  [default: /home/yourname/hello-bitcoin]
  --help                     Show this message and exit.
```

运行以下命令（可以不带命令行参数），生成2个账户、1笔交易和1个区块，并保存在输出路径中：

```
$ hello-bitcoin -a 2 -t 1 -b 1 -o ../output
```

生成`accounts.json`和`blocks.json`两个文件：

```json
// accounts.json
// 以地址作为索引
{
    "15natoEM1kLXDrGDRbGV3xVP22MhJK18ML": {
        "private key": "7c500f3d28d19f8849313b154b117ac8b2d9c24ee10030302fdf713018cae24d",
        "public key": "030814c477c32577eb767c5f13504bcc8e8f507aee536c8e24dda50e3f3506dd49"
    },
    "1E11jBYo2BGBqoaGpUQqifAHsS2QcpkKqs": {
        "private key": "d5e7d34525d4570a8d0543b62c0fb2a8c88ea1ca3693664446d8979f5c3332c9",
        "public key": "03bfb66dcab935fff3e331adab7d553c0e626bdd2519215a550003913db422d9d4"
    }
}
```

```json
// blocks.json
// 以区块hash作为索引
{
    "af7df63c74e8a122fa7cd344af3a6a5f5822f4afd90ef3a5e3933067b769b6cc": {
        "version": 1,
        "hash": "af7df63c74e8a122fa7cd344af3a6a5f5822f4afd90ef3a5e3933067b769b6cc",
        "previous block hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "merkle root": "167e07b8f25d3cfa585f9b685d35b1cf1b101021261bc34bf476ec5b20c4297b",
        "target": 0,
        "timestamp": 0,
        "nonce": 0,
        "tx": [
            {
                "hash": "167e07b8f25d3cfa585f9b685d35b1cf1b101021261bc34bf476ec5b20c4297b",
                "version": 1,
                "vin": [
                    {
                        "txid": "b7359e0ae5611b3034f87081fbe32f77558072d9f85a9a6853cae08675496caa",
                        "vout": 832961847,
                        "scriptSig": "483045022100a22cd7ae7b501d33f556c763c811bb71dcc85d145aa227d198e74e429c42e7940220185cad004fd6ff7d568e24599eb4ef43e309ee93d3876e9d0f648d8f1aa39303012103bfb66dcab935fff3e331adab7d553c0e626bdd2519215a550003913db422d9d4",
                        "sequence": "ffffffff"
                    }
                ],
                "vout": [
                    {
                        "value": "4.17215855",
                        "scriptPubKey": "76a914347f838fb2ea6dc3cc562f14eafa465b990641f988ac"
                    }
                ],
                "locktime": 0
            }
        ]
    }
}
```

在检查时，可以将`blocks.json`中的区块信息序列化后进行hash，与文件中的hash值进行比对。

## 代码说明

### `merkletree.py`

包含`MerkleNode`和`MerkleTree`两个类，调用`MerkleTree.make_merkle_tree(data)`即可生成一棵merkle树。merkle树构建算法参照了[*Mastering Bitcoin 2nd Edition*第205页](https://github.com/bitcoinbook/bitcoinbook/blob/develop/code/merkle.cpp)的C++实现。

### `account.py`

包含`Account`一个类，表示比特币账户，其中包含了账户的公钥、私钥和地址。`Account`类提供了两种生成方式，一种是随机生成`from_random_key`，另一种是从给定私钥生成`from_private_key`，后者目前只在测试中有使用。使用`Account`能对消息进行签名`sign`和验证`verify`。

这里使用了开源库[python-ecdsa](https://github.com/tlsfuzzer/python-ecdsa)来生成密钥对，并进行签名和验证。另外还使用了开源库[base58](https://github.com/keis/base58)来生成账户地址。由于base58库提供的base58check编码中没有添加version前缀，需自行在公钥的哈希前添加`0x00`。

### `transaction.py`

包含三个类：`TxIn`、`TxOut`和`Transaction`。每个类都提供相应的序列化和反序列化方法，这部分参照了[*Mastering Bitcoin 2nd Edition*](https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06.asciidoc)相关内容，以及[比特币官方项目测试代码中的实现](https://github.com/bitcoin/bitcoin/blob/master/test/functional/test_framework/messages.py)。另外为了便于阅读，还提供了字典转换的方法。

另外，`Transaction`类提供了`generate`方法，用于随机生成一笔交易，其中input中的签名和output中的公钥哈希都由参数指定：

- 在随机生成input时，会将随机字符串哈希后作为伪txid，并根据参数提供的账户生成签名和脚本；
- 在随机生成output时，会由参数提供的账户地址decode得到公钥的哈希，并组合成P2PKH脚本。

此外，文件中提供了`make_P2PKH_scriptPubKey`方法来生成公钥对应的P2PKH脚本，和`make_scriptSig`方法来将签名和公钥拼接成脚本。

### `block.py`

包含`BlockHeader`和`Block`两个类。其中的序列化和反序列化方法参考了[Bitcoin Developer Reference](https://btcinformation.org/en/developer-reference#serialized-blocks)和[比特币官方项目测试代码中的实现](https://github.com/bitcoin/bitcoin/blob/master/test/functional/test_framework/messages.py)。与`Transaction`一样，也提供了字典转换的方法。

`Block`和`Transaction`的反序列化方法事实上在作业中并不会用到，只会在测试时会用到。另外，`Block`提供的`is_valid`方法也只会在测试中用到，用来检查反序列化后的区块merkle根是否与真实区块一致。

### `utils.py`

包含了一些实用方法，具体见代码注释。

其中`ser_compact_size`和`deser_compact_size`的实现直接参照了[比特币官方项目测试代码中的实现](https://github.com/bitcoin/bitcoin/blob/master/test/functional/test_framework/messages.py#L74)，用于按照CompactSize Unsigned Integer编码格式序列化和反序列化。

### `main.py`

包含了一个`cli`方法，按照实验作业的要求，根据输入参数，生成若干个账户和若干个交易，用生成的账户对这些交易进行签名，再生成若干个区块将这些交易打包。最后把生成的结果输出到文件中。

### `setup.py`

用于配置Python `Click`模块。

### 测试

`hello-bitcon/test/`包含了本次作业的测试代码。测试只覆盖了一部分，不包括随机生成交易等等。

- `test_merkletree.py`：用随机字符串生成merkle树并验证父子节点之间的关系；
- `test_accout.py`：根据[*Mastering Bitcoin 2nd Edition*](https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch04.asciidoc#implementing-keys-and-addresses-in-c)中提供的数据，测试密钥对、地址生成算法的正确性，并测试了签名和验证的流程；
- `test_transaction.py`：根据[*Mastering Bitcoin 2nd Edition*](https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06.asciidoc)中提供的数据，测试交易的序列化和反序列化。因为无从知晓签名时的私钥，没有测试生成签名脚本的算法的正确性；
- `test_block.py`：利用[Blockchain Data API](https://blockchain.info/api/blockchain_api)获取真实区块信息，随机取高度在[0, 200000]内的区块来验证区块反序列化算法的正确性。因为API提供的交易信息不完全，只提供了交易在其数据库中的tx_index而非txid，无法测试区块的序列化算法。

想要进行测试，需要安装`pytest`模块：`pip install pytest`。安装完成后在代码目录下运行`pytest`即可。

## 实验中遇到的问题

- 字节、16进制字符串、整数之间的相互转换有点混乱，花了很多时间理清它们。
- 教材[*Mastering Bitcoin 2nd Edition*](https://github.com/bitcoinbook/bitcoinbook/)中对脚本的编码格式不够清晰，有一些字节的含义没有讲清楚，需要额外查阅资料。
- 比特币的字节表示方式有点混乱，交易hash得到的txid值使用大端序的16进制表示，而交易序列化时，输入部分的txid后则又反过来，造成了不小的困扰。
