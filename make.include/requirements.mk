# requirements - build requirements.txt 


requirements.txt: pyproject.toml
	tq -r '.project.dependencies|.[]' $< >$@

requirements-dev.txt: pyproject.toml
	tq -r '.project["optional-dependencies"].dev|.[]' $< >$@

requirements-docs.txt: pyproject.toml
	tq -r '.project["optional-dependencies"].docs|.[]' $< >$@
