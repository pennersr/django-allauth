from django.contrib.auth.hashers import PBKDF2PasswordHasher

from tests.projects.common.settings import IDP_OIDC_PRIVATE_KEY  # noqa
from tests.projects.common.settings import TEMPLATES  # noqa
from tests.projects.common.settings import INSTALLED_SOCIALACCOUNT_APPS


SECRET_KEY = "psst"
SITE_ID = 1
ALLOWED_HOSTS = (
    "testserver",
    "example.com",
)
USE_I18N = False
USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

ROOT_URLCONF = "tests.projects.login_required_mw.urls"
LOGIN_URL = "/accounts/login/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "tests.projects.login_required_mw.middleware.CustomLoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.usersessions",
    "allauth.headless",
    "allauth.idp.oidc",
) + INSTALLED_SOCIALACCOUNT_APPS

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

STATIC_ROOT = "/tmp/"  # Dummy
STATIC_URL = "/static/"


class MyPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    """
    A subclass of PBKDF2PasswordHasher that uses 1 iteration.

    This is for test purposes only. Never use anywhere else.
    """

    iterations = 1


PASSWORD_HASHERS = [
    "tests.projects.login_required_mw.settings.MyPBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "unittest-server",
                "name": "Unittest Server",
                "client_id": "Unittest client_id",
                "client_secret": "Unittest client_secret",
                "settings": {
                    "server_url": "https://unittest.example.com",
                },
            },
            {
                "provider_id": "other-server",
                "name": "Other Example Server",
                "client_id": "other client_id",
                "client_secret": "other client_secret",
                "settings": {
                    "server_url": "https://other.example.com",
                },
            },
        ],
    }
}

ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_ADAPTER = "tests.projects.common.adapters.AccountAdapter"

MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = True

HEADLESS_SERVE_SPECIFICATION = True
