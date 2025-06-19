Contributing to django-allauth
==============================

.. begin-contributing

Thank you for considering contributing to django-allauth! This document outlines the process for contributing to the project and sets up your development environment.

Code of Conduct
---------------

In the interest of fostering an open and welcoming community, we as contributors and maintainers pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

Getting Started
---------------

Setting Up Your Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two primary ways to set up your development environment:

Option 1: Standard Python Virtual Environment (Recommended for Beginners)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Install system dependencies**

   Before creating a virtual environment, you'll need to install some system dependencies:

   **On macOS:**

   .. code-block:: bash

      # Using Homebrew
      brew install libxml2 libxmlsec1 pkg-config openssl

   **On Ubuntu/Debian:**

   .. code-block:: bash

      sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config

   **On RHEL/CentOS/Fedora:**

   .. code-block:: bash

      sudo dnf install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel

2. **Create and activate a virtual environment**

   .. code-block:: bash

      # Create a virtual environment
      python -m venv virtualenv

      # Activate it
      # On Windows:
      virtualenv\Scripts\activate
      # On macOS/Linux:
      source virtualenv/bin/activate

3. **Install django-allauth in development mode**

   .. code-block:: bash

      # Install development dependencies
      pip install -r requirements-dev.txt

Option 2: Using devenv/Nix (Recommended for Advanced Users)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you prefer a more isolated and reproducible development environment, you can use Nix-based `devenv <https://devenv.sh>`_:

1. **Install devenv** (If you don't have it already)

   Follow the `official installation instructions <https://devenv.sh/getting-started/>`_.

2. **Activate the developer environment**

   .. code-block:: bash

      # This will create an isolated environment with all required dependencies
      devenv shell

   Note: The first time you run this command, it may take a significant amount of time as it builds all dependencies. Subsequent launches will be much faster.


Running Tests
-------------

django-allauth uses a comprehensive test suite. You can run tests in several ways:

Using pytest directly
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests for the default setup
   pytest allauth/

   # Run tests with a specific Django settings module
   pytest --ds=tests.projects.regular.settings tests/

   # Run a specific test file
   pytest tests/apps/account/test_login.py

Note, if you are using MacOS, using pip and get this error when run tests:

.. code-block:: bash

   import xmlsec
   ImportError: dlopen( ...  symbol not found in flat namespace '_xmlSecOpenSSLTransformHmacRipemd160GetKlass')

You can try:

.. code-block:: bash

   pip uninstall xmlsec lxml
   pip install --no-binary :all: xmlsec
   # Ref: https://github.com/xmlsec/python-xmlsec/issues/320

Using nox (recommended)
~~~~~~~~~~~~~~~~~~~~~~~

Nox automates testing across different Python and Django versions:

.. code-block:: bash

   # List all available sessions
   nox --list

   # Run tests for a specific Python version
   nox -x --session "test-3.11"

   # Run tests for specific environment
   nox -x --session "test-3.11" --python 3.11 -- --ds=tests.projects.regular.settings tests/apps/account/test_login.py

Run Code Quality Checks
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all linting checks
   nox -t lint

   # Run specific check
   nox --session black
   nox --session isort
   nox --session flake8
   nox --session mypy
   nox --session bandit
   nox --session djlint

Building Documentation
----------------------

Documentation is built using Sphinx:

.. code-block:: bash

   # Build the documentation
   nox --session docs

The built documentation will be available in the ``docs/_build/html`` directory.

Development Workflow
--------------------

1. **Create a new branch for your feature or bugfix**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes and add tests**

   All new features should include proper tests.

3. **Run tests locally to ensure everything passes**

   .. code-block:: bash

      nox -x --session "test-3.11"

4. **Run code quality checks**

   .. code-block:: bash

      nox -t lint

5. **Commit your changes with meaningful commit messages**

6. **Submit a pull request to the main repository**

Pull Request Guidelines
-----------------------

- Update documentation for significant changes
- Add tests for new functionality
- Ensure all tests pass
- Follow the project's code style
- Keep pull requests focused on a single topic
- Write clear, descriptive commit messages

Additional Resources
--------------------

- `Official Documentation <https://docs.allauth.org/en/latest/>`_
- `Issue Tracker <https://codeberg.org/allauth/django-allauth/issues>`_
- `Project Source <https://codeberg.org/allauth/django-allauth>`_

Thank you for your contributions!

.. end-contributing
