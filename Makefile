PYTHON = python

.PHONY: usage
usage:
	@echo 'Usage: make [target]'

.PHONY: po
po:
	( cd allauth ; $(PYTHON) ../manage.py makemessages -a -e html,txt,py )

.PHONY: mo
mo:
	( cd allauth ; $(PYTHON) ../manage.py compilemessages )

.PHONY: isort
isort:
	isort --check-only --diff allauth/ tests/

.PHONY: bandit
bandit:
	bandit -q -c pyproject.toml -r allauth/

.PHONY: black
black:
	black --check -q .

.PHONY: test
test:
	pytest allauth/


.PHONY: djlint
djlint:
	djlint --quiet --check allauth examples

.PHONY: flake8
flake8:
	flake8 allauth

.PHONY: qa
qa: validate-api-spec mypy djlint bandit black isort flake8

.PHONY: mypy
mypy:
	mypy allauth/

.PHONY: validate-api-spec
validate-api-spec:
	@if command -v swagger-cli >/dev/null 2>&1; then			\
		swagger-cli validate allauth/headless/spec/doc/openapi.yaml;	\
	else									\
		echo "WARNING: swagger-cli not found in PATH.";			\
	fi

.PHONY: ci
ci:
	woodpecker-cli exec .woodpecker.yaml


.PHONY: standardjs
standardjs:
	find ./allauth -name '*.js' | xargs ./node_modules/.bin/standard --ignore allauth/mfa/static/mfa/js/webauthn-json.js


.PHONY: docs
docs:
	$(MAKE) -C docs html

.PHONY: ci-install-standardjs
ci-install-standardjs:
	npm install standard --no-lockfile --no-progress --non-interactive --silent

.PHONY: clean
clean:
	-rm -rf build/ django_allauth.egg-info/

.PHONY: dist
dist: clean mo
	python -m build --sdist
	python -m build --wheel
