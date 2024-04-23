PYTHON = python

.PHONY: usage
usage:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@echo '  black         Auto format Python code'
	@echo '  isort         Fix isort issues'
	@echo '  po            (Re)generate .po files'
	@echo '  mo            Compile .po into .mo'
	@echo '  qa            Perform QA checks'
	@echo '  test          Execute test suite'

.PHONY: po
po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt,py )

.PHONY: mo
mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

.PHONY: isort
isort:
	isort .

.PHONY: black
black:
	black allauth/ setup.py

.PHONY: test
test:
	pytest allauth/

.PHONY: qa
qa: validate-api-spec
	flake8 allauth
	isort --check-only --diff .
	black --check .
	djlint --check allauth examples

.PHONY:
validate-api-spec:
	swagger-cli validate docs/_static/headless/openapi-specification/openapi.yaml
