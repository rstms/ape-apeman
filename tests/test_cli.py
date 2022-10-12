#!/usr/bin/env python

import json
from traceback import print_exception

import pytest
from click.testing import CliRunner

import ape_apeman
from ape_apeman import __version__, cli


def test_cli_version():
    """Test reading version and module name"""
    assert ape_apeman.__name__ == "ape_apeman"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    # env = os.environ.copy()
    # env['EXTRA_ENV_VAR'] = 'VALUE'

    def _run(cmd, **kwargs):
        expect_exit_code = kwargs.pop("expect_exit_code", 0)
        expect_exception = kwargs.pop("expect_exception", None)
        if expect_exception is None:
            kwargs["catch_exceptions"] = False

        # kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if result.exception:
            if expect_exception and isinstance(
                result.exception, expect_exception
            ):
                return result
            else:
                print_exception(result.exception)
                breakpoint()
                pass
        else:
            assert result.exit_code == expect_exit_code, result.output
        if expect_exception:
            raise RuntimeError(f"unraised {expect_exception=}")
        return result

    return _run


def test_cli_no_args(run):
    """Test the CLI."""
    result = run([])
    assert "Usage:" in result.output


def test_cli_help(run):
    result = run(["--help"])
    assert "Show this message and exit." in result.output


def test_cli_txn_url(run, txn_hash):
    result = run(["txn", "--url", txn_hash])
    url = json.loads(result.output)
    assert isinstance(url, str)
    assert url.startswith("https://")


TXN_KEYS = [
    "block_number",
    "gas_used",
    "logs",
    "status",
    "txn_hash",
    "transaction",
    "gas_limit",
    "gas_price",
]


def test_cli_txn_json(run, txn_hash):
    result = run(["txn", txn_hash])
    txn = json.loads(result.output)
    assert isinstance(txn, dict)
    assert set(txn.keys()) == set(TXN_KEYS)
