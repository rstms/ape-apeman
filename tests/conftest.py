import datetime
import json
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture(autouse=True)
def setup_logger():
    logging.basicConfig(
        format="%(levelname)s %(name)s.%(funcName)s: %(message)s [%(filename)s:%(lineno)s]",
        force=True,
    )
    logging.getLogger("urllib3.connectionpool").setLevel("WARNING")
    logging.getLogger("ape").setLevel("ERROR")


@pytest.fixture(scope="session", autouse=True)
def preserve_ape_data_dir():
    """backup and restore ape data and ape project data, keeping archive copy of state after tests"""
    ape_data_dir = Path.home().resolve() / ".ape"
    ape_project_dir = Path(".") / ".ape"
    test_archive_dir = (
        Path(".")
        / "test_ape_data"
        / datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )
    test_archive_dir.mkdir(parents=True)
    with TemporaryDirectory() as temp_dir:
        backup_ape_data_dir = Path(temp_dir) / "data"
        shutil.copytree(ape_data_dir, backup_ape_data_dir)
        shutil.rmtree(ape_data_dir)
        ape_data_dir.mkdir()
        backup_ape_project_dir = Path(temp_dir) / "projects"
        shutil.copytree(ape_project_dir, backup_ape_project_dir)
        shutil.rmtree(ape_project_dir)
        ape_project_dir.mkdir()
        try:
            yield True
        finally:
            shutil.copytree(ape_data_dir, test_archive_dir / "data")
            shutil.rmtree(ape_data_dir)
            shutil.copytree(backup_ape_data_dir, ape_data_dir)
            shutil.copytree(ape_project_dir, test_archive_dir / "projects")
            shutil.rmtree(ape_project_dir)
            shutil.copytree(backup_ape_project_dir, ape_project_dir)


@pytest.fixture
def test_contract_data(shared_datadir):
    contract_data_file = shared_datadir / "test_contract.json"
    return json.loads(contract_data_file.read_text())


@pytest.fixture
def contract_address(test_contract_data):
    return test_contract_data["address"]


@pytest.fixture
def contract_abi(test_contract_data):
    return test_contract_data["abi"]


@pytest.fixture
def abi_map_dict(contract_address, contract_abi):
    return {contract_address: contract_abi}


@pytest.fixture
def abi_map_file(abi_map_dict, shared_datadir):
    map_file = shared_datadir / "abi_map.json"
    map_file.write_text(json.dumps(abi_map_dict))
    return map_file


@pytest.fixture
def patched_env_ape_dirs(monkeypatch, shared_datadir, abi_map_file):
    monkeypatch.setenv("APE_PROJECT_DIR", str(shared_datadir / "ape_project"))
    monkeypatch.setenv("APE_DATA_DIR", str(shared_datadir / "ape_data"))
    yield True


@pytest.fixture
def patched_env_abi_file(monkeypatch, abi_map_file):
    monkeypatch.setenv("APE_ABI_FILE", str(abi_map_file))
    yield True


@pytest.fixture
def txn_hash():
    return "0x96823521c0c1999e4c1023279a1b4ef343649d37ac5f5b50a5fc7264064cb0ac"


@pytest.fixture
def owner_address():
    return "0x27566e752e56D403fB436C8b7031e7fcc75b6b4f"


@pytest.fixture
def owner_private_key():
    return os.environ["TEST_ACCOUNT_PRIVATE_KEY"]
