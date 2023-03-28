VIRTUALENV = $(shell pwd)/venv.tmp
PYTHON = $(VIRTUALENV)/bin/python

po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt,py )

mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

isort-fix:
	ruff --select=I .

.PHONY:						\
	po					\
	mo					\
	isort-fix
