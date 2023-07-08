PYTHON = python
ISORT = isort $$(find $(PWD)/allauth -not -path '*/migrations/*' -type f -name '*.py' -not -name '__init__.py' -print)


.PHONY: usage
usage:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@echo '  black         Auto format Python code'
	@echo '  isort         Fix isort issues'
	@echo '  po            (Re)generate .po files'
	@echo '  mo            Compile .po into .mo'

.PHONY: po
po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt,py )

.PHONY: mo
mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

.PHONY: isort
isort:
	$(ISORT)

.PHONY: black
black:
	black allauth/ setup.py

.PHONY: test
test:
	pytest allauth/
