import pytest
from io import BytesIO
from transaction import Transaction, TxIn, TxOut, make_P2PKH_scriptPubKey, make_scriptSig


@pytest.fixture()
def mock_tx_hex():
    """测试数据来自Mastering Bitcoin第二版第123页"""
    return '0100000001186f9f998a5aa6f048e51dd8419a14d8a0f1a8a2836dd73'\
           '4d2804fe65fa35779000000008b483045022100884d142d86652a3f47'\
           'ba4746ec719bbfbd040a570b1deccbb6498c75c4ae24cb02204b9f039'\
           'ff08df09cbe9f6addac960298cad530a863ea8f53982c09db8f6e3813'\
           '01410484ecc0d46f1918b30928fa0e4ed99f16a0fb4fde0735e7ade84'\
           '16ab9fe423cc5412336376789d172787ec3457eee41c04f4938de5cc1'\
           '7b4a10fa336a8d752adfffffffff0260e31600000000001976a914ab6'\
           '8025513c3dbd2f7b92a94e0581f5d50f654e788acd0ef800000000000'\
           '1976a9147f9b1a7fb68d60c536c2fd8aeaa53a8f3cc025a888ac00000000'


@pytest.fixture()
def mock_tx():
    """测试数据来自Mastering Bitcoin第二版第118页"""
    txin = TxIn(
        int('7957a35fe64f80d234d76d83a2a8f1a0d8149a41d81de548f0a65a8a999f6f18', 16),
        0,
        make_scriptSig(
            bytes.fromhex(
                '3045022100884d142d86652a3f47ba4746ec719bbfbd040a570b1deccbb6498c75c4ae2'
                '4cb02204b9f039ff08df09cbe9f6addac960298cad530a863ea8f53982c09db8f6e3813'
            ),
            '0484ecc0d46f1918b30928fa0e4ed99f16a0fb4fde0735e7ade8416ab9fe423cc'
            '5412336376789d172787ec3457eee41c04f4938de5cc17b4a10fa336a8d752adf'
        ),
        4294967295
    )
    txout1 = TxOut(
        int(0.01500000*100000000),
        make_P2PKH_scriptPubKey(bytes.fromhex('ab68025513c3dbd2f7b92a94e0581f5d50f654e7'))
    )
    txout2 = TxOut(
        int(0.08450000*100000000),
        make_P2PKH_scriptPubKey(bytes.fromhex('7f9b1a7fb68d60c536c2fd8aeaa53a8f3cc025a8'))
    )
    return Transaction(1, [txin], [txout1, txout2], 0)


def test_transaction_serialize(mock_tx_hex, mock_tx):
    assert mock_tx.serialize().hex() == mock_tx_hex


def test_transaction_deserialize(mock_tx_hex, mock_tx):
    assert Transaction.deserialize(
        BytesIO(bytes.fromhex(mock_tx_hex))
    ).to_dict() == mock_tx.to_dict()
