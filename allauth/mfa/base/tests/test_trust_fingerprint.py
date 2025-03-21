from allauth.mfa.internal.flows import trust
from allauth.mfa.models import Authenticator


def test_cookie_encoding():
    pass


def test_fingerprint_is_stable(user_with_totp, user_with_recovery_codes):
    fp = trust.create_config_fingerprint(user_with_totp)
    fp2 = trust.create_config_fingerprint(user_with_totp)
    assert fp == fp2


def test_fingerprint_changes_on_password_change(user_with_totp, password_factory):
    fp = trust.create_config_fingerprint(user_with_totp)
    user_with_totp.set_password(password_factory())
    fp2 = trust.create_config_fingerprint(user_with_totp)
    assert fp != fp2


def test_fingerprint_changes_on_recovery_codes_change(
    user_with_recovery_codes, password_factory
):
    fp = trust.create_config_fingerprint(user_with_recovery_codes)
    auth = Authenticator.objects.get(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    )
    auth.data["seed"] = password_factory()
    auth.save()
    fp2 = trust.create_config_fingerprint(user_with_recovery_codes)
    assert fp != fp2


def test_fingerprint_changes_on_new_authenticator(user_with_totp):
    fp = trust.create_config_fingerprint(user_with_totp)
    Authenticator.objects.create(
        user=user_with_totp, type=Authenticator.Type.RECOVERY_CODES, data={}
    )
    fp2 = trust.create_config_fingerprint(user_with_totp)
    assert fp != fp2


def test_fingerprint_changes_on_authenticator_deletion(
    user_with_totp, user_with_recovery_codes
):
    fp = trust.create_config_fingerprint(user_with_totp)
    Authenticator.objects.filter(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    ).delete()
    fp2 = trust.create_config_fingerprint(user_with_totp)
    assert fp != fp2
