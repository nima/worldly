venv: .venv/updated
requirements.txt: .venv; . .venv/bin/activate && pip3 freeze > $@
.venv:; virtualenv --python=python3.9.9 $@
.venv/updated: requirements.txt Makefile
	. .venv/bin/activate && pip3 install --upgrade pip
	. .venv/bin/activate && pip3 install --upgrade setuptools
	. .venv/bin/activate && pip3 install -r $<
	. .venv/bin/activate && pip3 install ipython autoreload vulture
	. .venv/bin/activate && pip3 install pandas scipy numpy
	. .venv/bin/activate && pip3 install datadotworld
	. .venv/bin/activate && pip3 freeze > $<
	touch $@
.PHONY: update

ipython:; . .venv/bin/activate && PYTHONSTARTUP=repl.py ipython
.PHONY: ipython
