# Submitting Pull Requests

## General

 - [ ] Make sure you use [semantic commit messages](https://seesparkbox.com/foundry/semantic_commit_messages).
       Examples: `"fix(google): Fixed foobar bug"`, `"feat(accounts): Added foobar feature"`.
 - [ ] All Python code must be 100% pep8 and isort clean.
 - [ ] JavaScript code should adhere to [StandardJS](https://standardjs.com).
 - [ ] If your changes are significant, please update `ChangeLog.rst`.
 - [ ] Feel free to add yourself to `AUTHORS`.
 
 ## Provider Specifics
 
 In case you add a new provider:
 
- [ ] Make sure unit tests are available.
- [ ] Add an entry of your provider in `test_settings.py::INSTALLED_APPS` and `docs/installation.rst::INSTALLED_APPS`.
- [ ] Add documentation to `docs/providers.rst`.
- [ ] Add an entry to the list of supported providers over at `docs/overview.rst`.
