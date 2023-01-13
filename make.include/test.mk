# test - testing with pytest and tox

options ?= -x --log-cli-level=CRITICAL $(if $(USE_GAS),, -m "not uses_gas")
testfiles ?= $(wildcard tests/test_*.py)
options := $(if $(test),$(options) -k $(test),$(options))

tox_options ?= -m "not uses_gas"


### run tests;  example: make options=-svvx test=cli test 
test:
	env TESTING=1 pytest $(options) $(testfiles)

### run tests; drop into pdb on exceptions or breakpoints
debug:
	env TESTING=1 pytest $(options) --log-cli-level=INFO -xvvvs --pdb $(testfiles)

### check code coverage quickly with the default Python
coverage:
	env TESTING=1 coverage run --source $(module) -m pytest
	coverage report -m
	coverage html
	$(browser) htmlcov/index.html

### list test cases
testls:
	@grep -h -R '^def test_' tests/test_*.py | awk -F'[ (]' '{print $$2}' | sort | uniq


.PHONY: tox
### test with tox if sources have changed
tox: .tox 
.tox: $(src) tox.ini fmt
	$(call gitclean)
	env PYTEST_OPTIONS='$(tox_options)' tox
	@touch $@

detox:
	$(MAKE) --no-print-directory ALLOW_DIRTY=1 tox

# run tox in debug mode
toxdebug:
	$(MAKE) --no-print-directory tox_options="-o log_cli_level=INFO -xvvvs --pdb" tox

toxclean:
	rm -rf .tox

test-clean: toxclean
