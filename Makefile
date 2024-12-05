repl ipython: venv dw; . .venv/bin/activate && PYTHONSTARTUP=repl.py ipython
.PHONY: ipython

build: pipenv.build venv
purge: pipenv.purge
rebuild: pipenv.purge pipenv.build

venv: .venv
.venv:; ln -sf $(shell pipenv --venv) $@
.PHONY: venv

pipenv.build: Pipfile.lock
Pipfile.lock: Pipfile
	pipenv install --python 3.12
	pipenv --python 3.12
	pipenv check
.PHONY: pipenv.build

pipenv.purge:
	pipenv --rm          # purge virtualenv entirely
	rm -rf Pipfile.lock  # purge the pipenv lockfile
	rm -f .venv          # remove reference to virtualenv
.PHONY: pipenv.purge

ifeq (DW_AUTH_TOKEN,)
dw: ${HOME}/.dw/config
${HOME}/.dw/config:
	open https://docs.data.world/en/59261-65580-1--Python.html
else
dw:
	@echo "DW Configured"
endif
