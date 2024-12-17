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
	isort --check-only --diff .

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
	swagger-cli validate allauth/headless/spec/doc/openapi.yaml

.PHONY: ci
ci:
	woodpecker-cli exec .woodpecker.yaml


.PHONY: standardjs
standardjs:
	find ./allauth -name '*.js' | xargs ./node_modules/.bin/standard --ignore allauth/mfa/static/mfa/js/webauthn-json.js


.PHONY: docs
docs:
	$(MAKE) -C docs html


.PHONY: ci-install-bandit
ci-install-bandit:
	pip install bandit==1.7.10

.PHONY: ci-install-black
ci-install-black:
	pip install black==24.4.0

.PHONY: ci-install-mo
ci-install-mo:
	apt-get update
	apt-get install -y --no-install-recommends gettext
	pip install .[mfa,socialaccount,openid,saml]

.PHONY: ci-install-standardjs
ci-install-standardjs:
	npm install standard --no-lockfile --no-progress --non-interactive --silent

.PHONY: ci-install-djlint
ci-install-djlint:
	pip install djlint==1.34.1

.PHONY: ci-install-docs
ci-install-docs:
	pip install Django Sphinx sphinx_rtd_theme

.PHONY: ci-install-flake8
ci-install-flake8:
	pip install flake8==7.1.1

.PHONY: ci-install-isort
ci-install-isort:
	pip install isort==5.13.2

.PHONY: ci-install-mypy
ci-install-mypy:
	pip install .[mfa,socialaccount,openid,saml]
	pip install				\
	  'django-stubs==5.0.2'			\
	  'mypy==1.10.0'			\
	  'pytest>=7.4'				\
	  'pytest-asyncio == 0.23.8'		\
	  'pytest-django>=4.5.2'		\
	  'types-requests==2.32.0.20240602'	\
	  'python3-saml>=1.15.0,<2.0.0'
