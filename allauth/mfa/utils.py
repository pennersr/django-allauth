from cryptography.fernet import Fernet

from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator


def encrypt(text):
    if not app_settings.FERNET_KEY:
        return text
    return Fernet(app_settings.FERNET_KEY).encrypt(text.encode("utf8")).decode("ascii")


def decrypt(encrypted_text):
    if not app_settings.FERNET_KEY:
        return encrypted_text
    return (
        Fernet(app_settings.FERNET_KEY)
        .decrypt(encrypted_text.encode("ascii"))
        .decode("utf8")
    )


def is_mfa_enabled(request, user):
    return Authenticator.objects.filter(user=user).exists()
