# test use from python code

import pytest


@pytest.fixture
def check_url():
    def _check_url(url):
        assert isinstance(url, str)
        assert url.startswith("https://")

    return _check_url


def test_module_context_manager(txn_hash, check_url):
    import ape_apeman

    with ape_apeman.APE() as chain:
        url = chain.provider.network.explorer.get_transaction_url(txn_hash)
    check_url(url)


def test_module_connect_init(txn_hash, check_url):
    from ape_apeman import APE

    ape = APE(connect=True)
    url = ape.explorer.get_transaction_url(txn_hash)
    check_url(url)


def test_module_connect_call(txn_hash, check_url):
    from ape_apeman import APE

    ape = APE()
    ape.connect()
    url = ape.explorer.get_transaction_url(txn_hash)
    check_url(url)
