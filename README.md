ape-apeman
==========

An opinionated alternative api for the most excellent eth-ape project.

- 12-factor compliant
- embeddable in a service
- independent of user interaction


![Image](https://img.shields.io/github/license/rstms/ape-apeman)

![Image](https://img.shields.io/pypi/v/ape-apeman.svg)

![Image](https://circleci.com/gh/rstms/ape-apeman/tree/master.svg?style=shield)

![Image](https://readthedocs.org/projects/ape-apeman/badge/?version=latest)

manager module facilitating use of eth-ape functions


* Free software: MIT license
* Documentation: https://ape-apeman.readthedocs.io.



Credits
-------

This is a merely a wrapper around [ApeWorX eth-ape](https://github.com/ApeWorX/ape)

This package was created with Cookiecutter and `rstms/cookiecutter-python-cli`, a fork of the `audreyr/cookiecutter-pypackage` project template.

[audreyr/cookiecutter](https://github.com/audreyr/cookiecutter)
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
[rstms/cookiecutter-python-cli](https://github.com/rstms/cookiecutter-python-cli)
```
Usage: apeman [OPTIONS] COMMAND [ARGS]...

Options:
  --version               Show the version and exit.
  -e, --ecosystem TEXT    [env var: APE_ECOSYSTEM; required]
  -n, --network TEXT      [env var: APE_NETWORK; required]
  -p, --provider TEXT     [env var: APE_PROVIDER; required]
  -d, --debug             debug mode
  -j, --json / -r, --raw  select output format
  -c, --compact           output compact json
  -h, --humanize          human-friendly (but lossy) output
  --help                  Show this message and exit.

Commands:
  balance  output account balance
  eth      expose web3.eth methods
  txn      output transaction receipt
```
