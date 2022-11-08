# ape context manager

import os
from pathlib import Path

import ape

from .account import KeyAccount


class APE:
    def __init__(
        self,
        ecosystem=None,
        network=None,
        provider=None,
        selector=None,
        connect=False,
        project_dir=None,
        data_dir=None,
    ):
        project_dir = Path(
            project_dir
            or os.environ.get("APE_PROJECT_DIR", Path.cwd() / "ape")
        )
        data_dir = Path(
            data_dir or os.environ.get("APE_DATA_DIR", project_dir / "data")
        )
        project_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)

        ape.config.DATA_FOLDER = data_dir
        ape.config.PROJECT_FOLDER = project_dir

        ape.project = ape.Project(project_dir)

        ape.config.load(force_reload=True)
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

            self.__all__ = ape.__all__

            for attr in ape.__all__:
                setattr(self, attr, getattr(ape, attr))

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

        return self

    def disconnect(self, *args, **kwargs):
        if self.connection:
            self.context_manager.__exit__(*args, **kwargs)
        self.connection = None

    def __enter__(self, *args, **kwargs):
        return self.connect(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        self.disconnect(*args, **kwargs)
