# top-level Makefile 

usage: short-help

### local install in editable mode for development
dev: uninstall 
	pip install --verbose --upgrade -e .[dev]

### install to the local environment from the source directory
install: 
	pip install --verbose --upgrade .

### remove module from the local python environment
uninstall: 
	pip install -U pip setuptools wheel flit
	pip uninstall -yqq $(module)

### remove all build, test, coverage and Python artifacts
clean: 
	for clean in $(call included,clean); do ${MAKE} $$clean; done
	rm -f .pyproject.toml.*

include $(wildcard make.include/*.mk)
