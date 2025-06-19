import os

import nox


@nox.session
def docs(session):
    session.install(
        "Django==5.2",
        "Sphinx>=7.4.7,<8",
        "sphinx_rtd_theme",
        "djangorestframework>=3.15.2,<4",
        "django-ninja>=1.3.0,<2",
        "snowballstemmer<3",  # https://github.com/sphinx-doc/sphinx/issues/13533
    )
    session.run("make", "docs")


@nox.session(tags=["lint"])
def lint(session):
    session.install("bandit")
    session.run("bandit", "-c", "pyproject.toml", "-r", "allauth/")


@nox.session(tags=["lint"])
def isort(session):
    session.install("isort==5.13.2")
    session.run("isort", "--check-only", "--diff", "--gitignore", ".")


@nox.session(tags=["lint"])
def flake8(session):
    session.install("flake8==7.2.0")
    session.run("flake8", "allauth/")


@nox.session(tags=["lint"])
def black(session):
    session.install("black==24.4.0")
    session.run("black", "--check", ".")


@nox.session(tags=["lint"])
def djlint(session):
    session.install("djlint==1.34.1")
    session.run(
        "djlint", "--configuration", ".djlintrc", "--check", "./allauth", "./examples"
    )


DJANGO_PYTHON_REQ = {
    "4.2.20": ("3.8", "3.9", "3.10", "3.11"),
    "5.0": ("3.10", "3.11", "3.12"),
    "5.1": ("3.10", "3.11", "3.12"),
    "5.2": ("3.10", "3.11", "3.12", "3.13"),
}
DJANGO_LTS = "5.2"


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"])
@nox.parametrize("django", list(DJANGO_PYTHON_REQ.keys()))
@nox.parametrize(
    "project", ["regular", "headless_only", "account_only", "login_required_mw"]
)
def test(session, django, project):
    django_version = tuple(map(int, django.split(".")))
    if django != DJANGO_LTS:
        last_django_python = DJANGO_PYTHON_REQ[django][-1]
        first_django_python = DJANGO_PYTHON_REQ[django][0]
        if session.python not in (first_django_python, last_django_python):
            print(
                f"Skipping: only current LTS is tested against python{session.python}, not Django {django}"
            )
            return

    if project == "login_required_mw" and django_version < (5, 1):
        print(f"Skipping: project {project} does not support Django {django}")
        return
    if session.python not in DJANGO_PYTHON_REQ[django]:
        print(f"Skipping: Django {django} does not support python{session.python}")
        return
    session.install(
        f"django=={django}",
        "pytest>=8.3.5,<9",
        "pytest-asyncio==0.23.8",
        "pytest-django>=4.11,<5",
        "Pillow>=9.0",
        "coverage==7.6.1",
        # SAML is disabled in CI
        # "python3-saml==1.16.0",
        # "xmlsec==1.3.14",
        # "lxml==5.2.1",
        "pyyaml>=6.0.2,<7",
        "psycopg2-binary>=2.9.10,<3",
        "djangorestframework>=3.15.2,<4",
        "django-ninja>=1.3.0,<2",
        "mypy==1.10.0",
        ".[mfa,openid,socialaccount,steam]",  # SAML is disabled in CI
    )
    session.run("/bin/sh", "-c", "cd allauth; python ../manage.py compilemessages")
    run_coveralls = (
        os.environ.get("GITHUB_TOKEN")
        and project == "regular"
        and django == "5.2"
        and session.python == "3.13"
    )
    if run_coveralls:
        session.install("coveralls")
    session.run(
        "coverage",
        "run",
        "-m",
        "pytest",
        f"--ds=tests.projects.{project}.settings",
        "tests/",
    )
    if run_coveralls:
        session.run("coveralls", "--service=github")
    if django == "5.1" and session.python == "3.13":
        session.install(
            "django-stubs==5.1.3",
            "types-requests==2.32.0.20240602",
        )
        session.run("mypy", "allauth")
