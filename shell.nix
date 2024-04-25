with import <nixpkgs> {};

stdenv.mkDerivation {
    name = "django-allauth";
    buildInputs = [
        black
        gettext
        isort
        djlint
        nodejs
        python310
        python310Packages.daphne
        python310Packages.debugpy
        python310Packages.django
        python310Packages.pyls-ruff
        python310Packages.pylsp-rope
        python310Packages.pytest
        python310Packages.pytest-cov
        python310Packages.pytest-django
        python310Packages.python-lsp-server
        python310Packages.python3-openid
        python310Packages.python3-saml
        python310Packages.qrcode
        python310Packages.requests-oauthlib
        python310Packages.ruff
        python310Packages.sphinx-rtd-theme
        python310Packages.tox
        sphinx
        twine
    ];
    shellHook = ''
        export PATH="$PWD/node_modules/.bin/:$PATH"
    '';
}
