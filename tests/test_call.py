# contract call tests

import logging
from pprint import pformat

import pytest
from ape.contracts import ContractInstance
from eth_utils import to_wei

from ape_apeman import APE
from ape_apeman.contract import ContractCallResult

info = logging.info

TIP_GWEI = 10


@pytest.fixture
def ape():
    with APE() as ape:
        yield ape


def test_call_lookup(ape, contract_address, contract_abi):
    contract = ape.get_contract(contract_address)
    assert isinstance(contract, ContractInstance)
    symbol = contract.symbol()
    assert symbol == "ETHERSIEVE"


@pytest.mark.tryfirst
@pytest.mark.uses_gas
def test_call_set(ape, contract_address, owner_address, owner_private_key):
    royalty_fee = 1000000000000000
    result = ape.call_contract(
        contract_address,
        "setMintRoyalty",
        royalty_fee,
        private_key=owner_private_key,
        max_priority_fee=ape.provider.priority_fee + to_wei(TIP_GWEI, "gwei"),
    )
    assert isinstance(result, ContractCallResult)
    info(pformat(result.ret))
    info(pformat(result.receipt))


@pytest.mark.uses_gas
def test_call_get_set(
    ape, contract_address, contract_abi, owner_address, owner_private_key
):
    # get the current prices
    ape.set_contract_abi(contract_address, contract_abi)
    pre_prices = ape.call_contract(
        contract_address, "getPrices", sender=owner_address
    )
    info(f"{pre_prices=}")
    assert pre_prices.ret.mintRoyalty == 1000000000000000
    assert pre_prices.receipt is None

    # set the royalty price
    ret_set = ape.call_contract(
        contract_address,
        "setMintRoyalty",
        13337,
        sender=owner_address,
        private_key=owner_private_key,
        autosign=True,
        max_priority_fee=ape.provider.priority_fee + to_wei(TIP_GWEI, "gwei"),
    )
    assert ret_set.ret is None
    assert ret_set.receipt

    # get the changed price
    tmp_prices = ape.call_contract(
        contract_address, "getPrices", sender=owner_address
    )
    info(f"{tmp_prices=}")
    assert tmp_prices.ret.mintRoyalty == 13337
    assert tmp_prices.receipt is None

    # reset the price back to the original value
    ret_reset = ape.call_contract(
        contract_address,
        "setMintRoyalty",
        pre_prices.ret.mintRoyalty,
        private_key=owner_private_key,
        autosign=True,
        max_priority_fee=ape.provider.priority_fee + to_wei(TIP_GWEI, "gwei"),
    )
    assert ret_reset.ret is None
    assert ret_reset.receipt

    # finally test that the price is restored to original value
    post_prices = ape.call_contract(
        contract_address, "getPrices", sender=owner_address
    )
    info(f"{post_prices=}")
    assert post_prices.ret.mintRoyalty == pre_prices.ret.mintRoyalty
    assert post_prices.receipt is None


@pytest.mark.uses_gas
def test_call_mint(
    ape, contract_address, contract_abi, owner_address, owner_private_key
):
    uri = "ipfs://bafkreie5npehcwbdbog3j4w7otw22jzm6szsjtihtjnhc5oxhvwukhczgm"
    result = ape.call_contract(
        contract_address,
        "safeMint",
        owner_address,
        uri,
        private_key=owner_private_key,
        max_priority_fee=ape.provider.priority_fee + to_wei(TIP_GWEI, "gwei"),
        abi=contract_abi,
    )
    assert isinstance(result, ContractCallResult)
    info(pformat(result.dict()))
