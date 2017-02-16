VIRTUALENV = $(shell pwd)/venv.tmp
PYTHON = $(VIRTUALENV)/bin/python
ISORT = isort $$(find $(PWD)/allauth -not -path '*/migrations/*' -type f -name '*.py' -not -name '__init__.py' -print)

po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt,py )

mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

docs:
	( . $(VIRTUALENV)/bin/activate; cd docs; make html )

isort-check:
	$(ISORT) -c

isort-fix:
	$(ISORT)

pep8:
	flake8 --exclude=migrations allauth

standardjs:
	standard $$(find $(PWD)/allauth -name '*.js' -print)

qa: isort-check pep8 standardjs

.PHONY:						\
	po					\
	mo					\
	docs					\
	isort-fix				\
	isort-check				\
	pep8					\
	standard				\
	qa
