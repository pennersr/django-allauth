{ pkgs, lib, config, inputs, ... }:

{
  packages = [
    pkgs.git
    pkgs.swagger-cli
    pkgs.twine
    pkgs.woodpecker-cli
    pkgs.xmlsec
    pkgs.gettext

    pkgs.python312Packages.pyls-flake8
    pkgs.python312Packages.pylsp-rope
    pkgs.python312Packages.python-lsp-server
    pkgs.python312Packages.xmlsec
    pkgs.python312Packages.build
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    package = pkgs.python312;
    venv.enable = true;
    venv.requirements = ''
      -r ${./.}/requirements-dev.txt
    '';
  };

  enterShell = ''
    source $VIRTUAL_ENV/bin/activate
  '';
}
