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
        python310Packages.django
        python310Packages.flake8
        python310Packages.debugpy
        python310Packages.pycodestyle
        python310Packages.pyls-flake8
        python310Packages.pylsp-rope
        python310Packages.pytest
        python310Packages.pytest-cov
        python310Packages.pytest-django
        python310Packages.python-lsp-server
        python310Packages.python3-openid
        python310Packages.python3-saml
        python310Packages.qrcode
        python310Packages.sphinx-rtd-theme
        python310Packages.requests-oauthlib
        python310Packages.tox
        python310Packages.daphne
        sphinx
        twine
    ];
    shellHook = ''
        export PATH="$PWD/node_modules/.bin/:$PATH"
    '';
}
