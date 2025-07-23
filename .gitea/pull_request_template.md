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
- [ ] Ensure your provider is tested by adding an entry over at `tests/projects/common/settings.py::INSTALLED_SOCIALACCOUNT_APPS`.
- [ ] Provide provider specific documentation at `docs/socialaccount/providers/<provider name>.rst`.
- [ ] Link to your provider specific documentation at `docs/insocialaccount/providers/index.rst`.
- [ ] Add an entry for your provider in the quickstart, over at `docs/installation/quickstart.rst::INSTALLED_APPS`.