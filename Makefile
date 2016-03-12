VIRTUALENV = $(shell pwd)/venv.tmp
PYTHON = $(VIRTUALENV)/bin/python

po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt )

mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

.PHONY: \
	po \
	mo
