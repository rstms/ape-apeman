# version - automatic version management
 
# - Prevent version changes with uncommited changes
# - tag and commit version changes
# - Use 'lightweight tags'

define BUMPVERSION_CFG
[bumpversion]
current_version = $(version)
commit = True
tag = True
[bumpversion:file:$(module)/version.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"
endef

export BUMPVERSION_CFG

bumpversion = bumpversion --allow-dirty $(1) && git push

bump: bump-patch

### bump patch version
bump-patch: version-update
	$(call bumpversion,patch)

### bump minor version, reset patch to zero
bump-minor: version-update
	$(call bumpversion,minor)
	
### bump major version, reset minor and patch to zero
bump-major: version-update
	$(call bumpversion,major)

# assert gitclean, rewrite requirements.txt, update timestamp, apply version update
version-update: 
	$(call gitclean)
	[ -f .bumpversion.cfg ] || { echo "$$BUMPVERSION_CFG" >.bumpversion.cfg; git add .bumpversion.cfg; }
	$(MAKE) requirements.txt requirements-dev.txt requirements-docs.txt
	sed -E -i $(module)/version.py -e "s/(.*__timestamp__.*=).*/\1 \"$$(date --rfc-3339=seconds)\"/"
	git add $(module)/version.py
	git add requirements*.txt
	@echo "Updated version.py timestamp and requirements.txt"

# clean up version tempfiles
version-clean:
	@:

