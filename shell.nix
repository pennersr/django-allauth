with import <nixpkgs> {};

stdenv.mkDerivation {
    name = "django-allauth";
    buildInputs = [
        black
        gettext
        isort
        djlint
        python311
        python311Packages.bandit
        python311Packages.mypy
        python311Packages.django-stubs
        python311Packages.types-requests
        python311Packages.django
        python311Packages.djangorestframework
        python311Packages.flake8
        python311Packages.debugpy
        python311Packages.django-ninja
        python311Packages.pycodestyle
        python311Packages.pyls-flake8
        python311Packages.pylsp-rope
        python311Packages.pytest
        python311Packages.pytest-cov
        python311Packages.pytest-django
        python311Packages.pytest-asyncio
        python311Packages.python-lsp-server
        python311Packages.python3-openid
        python311Packages.python3-saml
        python311Packages.pyjwt
        python311Packages.psycopg
        python311Packages.qrcode
        python311Packages.sphinx-rtd-theme
        python311Packages.requests-oauthlib
        python311Packages.tox
        python311Packages.daphne
        python311Packages.fido2
        sphinx
        twine

        nodejs
        playwright-test

        swagger-cli
        woodpecker-cli
    ];
    shellHook = ''
        export PATH="$PWD/node_modules/.bin/:$PATH"
    '';
}
