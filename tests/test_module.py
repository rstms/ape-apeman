# test use from python code

import pytest
from ape_ethereum.transactions import Receipt

from ape_apeman import APE


@pytest.fixture
def check_url():
    def _check_url(url):
        assert isinstance(url, str)
        assert url.startswith("https://")

    return _check_url


@pytest.fixture
def check_receipt():
    def _check_receipt(receipt):
        assert isinstance(receipt, Receipt)

    return _check_receipt


@pytest.fixture
def check_block_number():
    def _check_block_number(block_number):
        assert isinstance(block_number, int)
        assert block_number > 1

    return _check_block_number


def test_module_context_url(txn_hash, check_url):
    with APE() as ape:
        url = ape.explorer.get_transaction_url(txn_hash)
    check_url(url)


def test_module_init_url(txn_hash, check_url):
    ape = APE(connect=True)
    url = ape.explorer.get_transaction_url(txn_hash)
    check_url(url)


def test_module_connect_url(txn_hash, check_url):
    ape = APE()
    ape.connect()
    url = ape.explorer.get_transaction_url(txn_hash)
    check_url(url)


def test_module_context_receipt(txn_hash, check_receipt):
    with APE() as ape:
        receipt = ape.provider.get_receipt(txn_hash)
    check_receipt(receipt)


def test_module_init_receipt(txn_hash, check_receipt):
    ape = APE(connect=True)
    receipt = ape.provider.get_receipt(txn_hash)
    check_receipt(receipt)


def test_module_connect_receipt(txn_hash, check_receipt):
    ape = APE()
    ape.connect()
    receipt = ape.provider.get_receipt(txn_hash)
    check_receipt(receipt)


def test_module_context_web3(check_block_number):
    with APE() as ape:
        n = ape.web3.eth.get_block_number()
    check_block_number(n)


def test_module_init_web3(check_block_number):
    ape = APE(connect=True)
    n = ape.web3.eth.get_block_number()
    check_block_number(n)


def test_module_connect_web3(check_block_number):
    ape = APE()
    ape.connect()
    n = ape.web3.eth.get_block_number()
    check_block_number(n)
