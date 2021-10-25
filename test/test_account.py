from account import Account


def test_account_key():
    """测试数据来自Mastering Bitcoin第二版第78页"""
    prik = '3aba4162c7251c891207b747840551a71939b0de081f85c4e44cf7c13e41daa6'
    pubk = '045c0de3b9c8ab18dd04e3511243ec2952002dbfadc864b9628910169d9b9b00ec243bcefdd4347074d44bd7356d6a53c495737dd96295e2a9374bf5f02ebfc176'
    a = Account.from_private_key(prik, public_key_encoding='uncompressed')
    assert a.public_key == pubk


def test_account_address():
    """测试数据来自Mastering Bitcoin第二版第69页"""
    prik = '038109007313a5807b2eccc082c8c3fbb988a973cacf1a7df9ce725c31b14776'
    addr = '1PRTTaJesdNovgne6Ehcdu1fpEdX7913CK'
    a = Account.from_private_key(prik, public_key_encoding='compressed')
    assert a.address == addr


def test_account_sign_verify():
    a = Account.from_random_key()
    m = b'blockchain-ss-2021'
    sig = a.sign(m)
    assert a.verify(sig, m) == True
    assert a.verify(sig, b'blockchain-ss-2O21') == False
    assert a.verify(a.sign(b'blockchain-ss-2O21'), m) == False
