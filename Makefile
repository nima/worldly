.DEFAULT_GOAL := status
.DEFAULT:
	@echo "Target '$@' is not defined in this Makefile."

serve: ollama.serve
build: pipenv.build venv
purge: pipenv.purge
rebuild: pipenv.clean pipenv.build
status: PIPAPI_PYTHON_LOCATION := $(shell pipenv --venv)/bin/python
status:
	pipenv check
	pipenv run safety scan
	pipenv run pip-audit
	pipenv run pip --disable-pip-version-check list --outdated
upgrade: rebuild pipenv.upgrade
	@#$(foreach pkg,$(shell pip --disable-pip-version-check list --outdated --format=json|jq -r 'map(.name)[]'),pipenv run pip install --upgrade ${pkg};)
	pipenv update
	pipenv upgrade
.PHONY: serve build purge rebuild status upgrade

################################################################################
# Interactive
repl ipython: PYTHONSTARTUP := repl.py
repl ipython: venv dw; pipenv run ipython
.PHONY: repl ipython

ollama: ollama.run
.PHONY: ollama

################################################################################
# Python Pipenv & VirtualEnv
pipenv.upgrade:
	@#pipenv run pip install --upgrade pip pipenv
	$(shell pipenv --venv)/bin/pip install --upgrade pip pipenv
.PHONY: pipenv.upgrade

pipenv.build: Pipfile.lock
Pipfile.lock: Pipfile
	pipenv install --python 3.12
	pipenv --python 3.12
.PHONY: pipenv.build

pipenv.clean:
	rm -f Pipfile.lock  # purge the pipenv lockfile
.PHONY: pipenv.clean

pipenv.purge: pipenv.clean
	pipenv --rm          # purge virtualenv entirely
	rm -f .venv          # remove reference to virtualenv
.PHONY: pipenv.purge

venv: .venv
.venv:; ln -sf $(shell pipenv --venv) $@
.PHONY: venv

################################################################################
# Local LLM Engines
ollama.pull:
	ollama pull llama3
	ollama pull mistral
.PHONY: ollama.pull

ollama.serve:
	ollama serve
.PHONY: ollama.serve

ollama.run:
	ollama run llama3
.PHONY: ollama.run

################################################################################
# Data World
ifeq (DW_AUTH_TOKEN,)
dw: ${HOME}/.dw/config
${HOME}/.dw/config:
	open https://docs.data.world/en/59261-65580-1--Python.html
else
dw:
	@echo "DW Configured"
endif
