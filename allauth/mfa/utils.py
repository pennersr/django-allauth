from allauth.account.authentication import record_authentication
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


def encrypt(text):
    return get_adapter().encrypt(text)


def decrypt(encrypted_text):
    return get_adapter().decrypt(encrypted_text)


def is_mfa_enabled(user, types=None):
    if user.is_anonymous:
        return False
    qs = Authenticator.objects.filter(user=user)
    if types is not None:
        qs = qs.filter(type__in=types)
    return qs.exists()


def post_authentication(request, authenticator):
    authenticator.record_usage()
    extra_data = {
        "id": authenticator.pk,
        "type": authenticator.type,
    }
    record_authentication(request, "mfa", **extra_data)
