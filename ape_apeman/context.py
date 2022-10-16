# ape context manager

import os

import ape


class APE:
    def __init__(
        self,
        ecosystem=None,
        network=None,
        provider=None,
        selector=None,
        connect=False,
    ):
        if selector is None:
            ecosystem = ecosystem or os.environ["APE_ECOSYSTEM"]
            network = network or os.environ["APE_NETWORK"]
            provider = provider or os.environ["APE_PROVIDER"]
            selector = os.environ.get(
                "APE_SELECTOR", f"{ecosystem}:{network}:{provider}"
            )
        self.context_manager = ape.networks.parse_network_choice(selector)
        self.connection = None
        if connect is True:
            self.connect()

    def __del__(self):
        if self.connection:
            self.disconnect()

    def connect(self, *args, **kwargs):
        if self.connection is None:
            self.connection = self.context_manager.__enter__(*args, **kwargs)
            self.provider = self.connection
            self.network = self.provider.network
            self.explorer = self.provider.network.explorer
            self.web3 = self.provider.web3
            self.contracts = self.network.chain_manager.contracts
        return self

    def disconnect(self, *args, **kwargs):
        if self.connection:
            self.context_manager.__exit__(*args, **kwargs)
        self.connection = None

    def __enter__(self, *args, **kwargs):
        return self.connect(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        self.disconnect(*args, **kwargs)
