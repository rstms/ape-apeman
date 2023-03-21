# test use from python code

import logging
from pathlib import Path
from pprint import pformat
from subprocess import run

import pytest
from ape_ethereum.transactions import Receipt
from eth_account import Account
from eth_utils import is_same_address

import ape_apeman.json as json
from ape_apeman import APE

info = logging.info
warning = logging.warning


@pytest.fixture(params=["context", "init", "connect"])
def ape(patched_env_ape_dirs, patched_env_abi_file, request):
    if request.param == "context":
        with APE() as ape:
            yield ape
    elif request.param == "init":
        ape = APE(connect=True)
        yield ape
    elif request.param == "connect":
        ape = APE()
        ape.connect()
        yield ape
    else:
        breakpoint()
        pass


def test_module_get_transaction_url(ape, txn_hash):
    if ape.explorer:
        info("calling explorer get_transaction_url")
        url = ape.explorer.get_transaction_url(txn_hash)
        assert isinstance(url, str)
        assert url.startswith("https://")
    else:
        warning("ape explorer not available")


def test_module_get_receipt(ape, txn_hash):
    receipt = ape.provider.get_receipt(txn_hash)
    assert isinstance(receipt, Receipt)


def test_module_web3_get_block_number(ape):
    block_number = ape.web3.eth.get_block_number()
    assert isinstance(block_number, int)
    assert block_number > 1


def test_module_contract(ape, contract_address):
    info(f"{contract_address=}")
    contract = ape.get_contract(contract_address)
    assert contract
    info(f"{contract=}")
    symbol = contract.symbol()
    info(f"{symbol=}")
    assert symbol == "ETHERSIEVE"


@pytest.mark.uses_gas
def test_module_sign_and_send(
    ape, contract_address, owner_address, owner_private_key
):
    account = Account().from_key(owner_private_key)
    assert account.address == owner_address
    contract = ape.get_contract(contract_address)
    nonce_before = ape.provider.get_nonce(account.address)
    txn = contract.getPrices.as_transaction(
        sender=account.address,
        required_confirmations=1,
        max_priority_fee="10 gwei",
    )
    txn.nonce = ape.provider.get_nonce(account.address)
    txn.signature = account.sign_transaction(txn.dict())
    receipt = ape.provider.send_transaction(txn)
    assert isinstance(receipt, Receipt)
    info(json.dumps(receipt.dict(), humanize=True))
    prices = receipt.return_value
    assert isinstance(prices.mintFee, int)
    assert isinstance(prices.mintRoyalty, int)
    assert isinstance(prices.mintGas, int)
    info(f"{receipt.return_value=}")
    nonce_after = ape.provider.get_nonce(account.address)
    assert nonce_before != nonce_after


def pdebug(object):
    logging.debug(pformat(object))


def _find_files(dir, label=None, output=pdebug):
    dir = Path(dir).resolve()
    label = label or str(dir)
    proc = run(
        ["find", str(dir), "-type", "f"],
        check=True,
        text=True,
        capture_output=True,
    )
    assert not proc.stderr
    files = proc.stdout.strip().split("\n")
    if output:
        output({label: files})
    return files


def test_module_account_call(
    ape, shared_datadir, contract_address, owner_address, owner_private_key
):
    # call a public function

    contract = ape.get_contract(contract_address)
    symbol = contract.symbol()
    assert symbol == "ETHERSIEVE"

    # call a function requiring authorized caller address
    with pytest.raises(ape.ape_exceptions.ContractError) as exc:
        components = contract.getComponents()
    assert "is missing role" in str(exc.value)

    # specify the public address in the lookup
    components = contract.getComponents(sender=owner_address)
    assert components

    # create an ape account
    account = ape.account(private_key=owner_private_key)
    assert is_same_address(account.address, owner_address)

    # with account.autosign_enabled():
    components = contract.getComponents(sender=account.address)
    assert components

    prices = contract.getPrices(sender=account.address)
    assert prices

    with account:
        prices = contract.getPrices(sender=account.address)
    assert prices

    with account.autosign_enabled():
        prices = contract.getPrices(sender=account.address)
    assert prices

    info(pformat(components))
    info(pformat(prices))
