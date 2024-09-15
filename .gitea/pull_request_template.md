# Submitting Pull Requests

## General

 - [ ] Make sure you use [semantic commit messages](https://seesparkbox.com/foundry/semantic_commit_messages).
       Examples: `"fix(google): Fixed foobar bug"`, `"feat(accounts): Added foobar feature"`.
 - [ ] All Python code must formatted using Black, and clean from pep8 and isort issues.
 - [ ] JavaScript code should adhere to [StandardJS](https://standardjs.com).
 - [ ] If your changes are significant, please update `ChangeLog.rst`.
 - [ ] If your change is substantial, feel free to add yourself to `AUTHORS`.

 ## Provider Specifics

 In case you add a new provider:

- [ ] Make sure unit tests are available.
- [ ] Add an entry of your provider in `test_settings.py::INSTALLED_APPS` and `docs/installation.rst::INSTALLED_APPS`.
- [ ] Add documentation to `docs/providers/<provider name>.rst` and `docs/providers/index.rst` Provider Specifics toctree.
- [ ] Add an entry to the list of supported providers over at `docs/overview.rst`.
