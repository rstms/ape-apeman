# eth-ape wrangler

import atexit
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

# from ape.exceptions import ChainError
from eth_utils import is_same_address, to_normalized_address
from ethpm_types.contract_type import ContractType

from . import exceptions
from .account import KeyAccount
from .contract import ContractCallResult

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("APEMAN_LOG_LEVEL", "WARNING"))


class APE:

    ape = None

    def __init__(
        self,
        ecosystem=None,
        network=None,
        provider=None,
        selector=None,
        connect=False,
        project_dir=None,
        data_dir=None,
        abi_map=None,
    ):
        if self.__class__.ape is None:
            import ape

            self.__class__.ape = ape

        self.exceptions = exceptions
        self.ape_exceptions = self.ape.exceptions
        self.connection = None
        self.contract_abi = {}
        self.set_abi_map(abi_map)
        self.project_dir = self.init_dir(project_dir, "APE_PROJECT_DIR")
        self.data_dir = self.init_dir(data_dir, "APE_DATA_DIR")

        self.ape.config.DATA_FOLDER = self.data_dir
        self.ape.config.PROJECT_FOLDER = self.project_dir

        self.ape.project = self.ape.Project(self.project_dir)

        self.ape.config.load(force_reload=True)
        if selector is None:
            ecosystem = ecosystem or os.environ["APE_ECOSYSTEM"]
            network = network or os.environ["APE_NETWORK"]
            provider = provider or os.environ["APE_PROVIDER"]
            selector = os.environ.get(
                "APE_SELECTOR", f"{ecosystem}:{network}:{provider}"
            )
        self.context_manager = self.ape.networks.parse_network_choice(selector)
        if connect is True:
            self.connect()

    def set_abi_map(self, abi_map=None):
        """set contract abi mapping from dict or filename"""
        abi_map = abi_map or os.environ.get("APE_ABI_FILE", None)
        if isinstance(abi_map, (str, Path)):
            abi_map = json.loads(Path(abi_map).read_text())
        if abi_map:
            for address, abi in abi_map.items():
                self.set_contract_abi(address, abi)

    def get_contract(
        self, contract_address, contract_type=None, txn_hash=None, abi=None
    ):
        if abi:
            self.set_contract_abi(contract_address, abi)
        try:
            contract = self.ape.Contract(
                contract_address, contract_type, txn_hash
            )
        except self.ape.exceptions.ChainError as exc:
            if exc.args[0].startswith(
                "Failed to get contract type for address"
            ):
                contract = self.ape.Contract(
                    contract_address,
                    ContractType(abi=self.get_contract_abi(contract_address)),
                    txn_hash,
                )
            else:
                raise exc from exc
        return contract

    def get_contract_abi(self, contract_address):
        """lookup cached contract_type for contract addresss"""
        contract_address = to_normalized_address(contract_address)
        try:
            abi = self.contract_abi[contract_address]
        except KeyError:
            raise self.exceptions.UnknownContractABI(f"{contract_address=}")
        return abi

    def init_dir(self, param, key):
        dir = param or os.environ.get(key)
        if dir:
            dir = Path(dir)
            dir.mkdir(exist_ok=True)
        else:
            dir = Path(tempfile.mkdtemp()).resolve()
            atexit.register(shutil.rmtree, str(dir))
            logger.debug(f"created temp directory {str(dir)} as {key}")

        if isinstance(dir, Path) is False or dir.is_dir() is False:
            raise TypeError(f"{dir} is not a directory")
        dir.chmod(0o700)
        return dir

    def __del__(self):
        if self.connection:
            self.disconnect()

    def account(
        self,
        private_key,
        alias=None,
        password=None,
        autosign=False,
    ):
        return KeyAccount(
            ape=self,
            private_key=private_key,
            alias=alias,
            password=password,
            autosign=autosign,
        )

    def connect(self, *args, **kwargs):
        if self.connection is None:

            self.connection = self.context_manager.__enter__(*args, **kwargs)

            self.__all__ = self.ape.__all__

            for attr in self.ape.__all__:
                setattr(self, attr, getattr(self.ape, attr))

            self.provider = self.connection
            self.network = self.connection.network
            self.explorer = self.provider.network.explorer
            self.web3 = self.provider.web3
            self.contracts = self.network.chain_manager.contracts

            # assert self.provider is self.project.provider
            # assert self.network is self.project.provider.network
            # assert self.explorer is self.project.provider.network.explorer
            # assert self.web3 is self.project.provider.web3
            # assert self.contracts is self.project.provider.network.chain_manager.contracts

            logger.debug(f"connected: {self}")

        return self

    def disconnect(self, *args, **kwargs):
        if self.connection:
            self.context_manager.__exit__(*args, **kwargs)
            logger.debug(f"disconnected: {self}")
        self.connection = None

    def __enter__(self, *args, **kwargs):
        return self.connect(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        self.disconnect(*args, **kwargs)

    def set_contract_abi(self, contract_address, abi):
        """set abi for contract address"""
        self.contract_abi[to_normalized_address(contract_address)] = abi

    def call_contract(self, contract_address, function_name, *args, **kwargs):
        """call a lookup or mutable contract function, returning a ContractCallResult

        kwargs:
          sender (ADDRESS if lookup, PRIVATE_KEY if mutable/transaction
          autosign: (bool) automatically sign transaction
          max_fee:  max fee per GAS to be used
          max_priority_fee: specify amount of 'tip' per GAS
          abi: (list) contract ABI
        """
        result = ContractCallResult()
        contract = self.get_contract(
            contract_address, abi=kwargs.pop("abi", None)
        )
        function = getattr(contract, function_name)
        if isinstance(function, self.ape.contracts.base.ContractCallHandler):
            # lookup call may include sender=ADDRESS
            result.ret = function(*args, **kwargs)
        elif isinstance(
            function, self.ape.contracts.base.ContractTransactionHandler
        ):
            # mutable call uses transaction, sender must be a private_key
            sender = kwargs.pop("sender", None)
            private_key = kwargs.pop("private_key", None)
            account = kwargs.pop("account", None)
            if private_key:
                account = self.account(private_key=private_key)

            elif account:
                account = account
            else:
                raise ValueError(
                    "mutable call requires 'private_key' or 'account'"
                )

            account.autosign = kwargs.pop("autosign", True)

            if sender is not None:
                if not is_same_address(sender, account.address):
                    raise ValueError(
                        f"account key mismatches sender address {sender}"
                    )

            with account as ape_account:
                receipt = function(*args, **kwargs, sender=ape_account)
                result.set_receipt(receipt)

        else:
            raise TypeError(
                f"function {function_name} not found in contract at {contract_address}"
            )

        return result
