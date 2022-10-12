# ape context manager

import os

import ape


class APE:
    def __init__(
        self, ecosystem=None, network=None, provider=None, connect=False
    ):
        ecosystem = ecosystem or os.environ["APE_ECOSYSTEM"]
        network = network or os.environ["APE_NETWORK"]
        provider = provider or os.environ["APE_PROVIDER"]
        selector = f"{ecosystem}:{network}:{provider}"
        self.context = ape.networks.parse_network_choice(selector)
        if connect is True:
            self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.context.provider.connect()
        self._set_properties(self.context.provider)
        return self

    def _set_properties(self, provider):
        self.provider = provider
        self.network = provider.network
        self.explorer = provider.network.explorer
        self.web3 = provider.web3

    def disconnect(self):
        self.context.provider.disconnect()

    def __enter__(self):
        self.context.__enter__()
        return self.connect()

    def __exit__(self, _, ex, tb):
        self.context.__exit__(_, ex, tb)
        self.disconnect()
