from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes


def test_flow(user):
    rc = RecoveryCodes.activate(user)
    codes = rc.generate_codes()
    assert len(set(codes)) == app_settings.RECOVERY_CODE_COUNT
    for code in codes:
        assert len(code) == app_settings.RECOVERY_CODE_DIGITS
    for i in range(app_settings.RECOVERY_CODE_COUNT):
        assert not rc._is_code_used(i)
    idx = 3
    assert rc.validate_code(codes[idx])
    for i in range(app_settings.RECOVERY_CODE_COUNT):
        assert rc._is_code_used(i) == (i == idx)
    assert not rc.validate_code(codes[idx])

    unused_codes = rc.get_unused_codes()
    assert codes[idx] not in unused_codes
    assert len(unused_codes) == app_settings.RECOVERY_CODE_COUNT - 1


def test_migrated_codes(db, user):
    auth = Authenticator(user=user, data={"migrated_codes": ["abc", "def"]})
    rc = RecoveryCodes(auth)
    assert rc.generate_codes() == ["abc", "def"]
    assert rc.get_unused_codes() == ["abc", "def"]
    assert not rc.validate_code("bad")
    assert rc.validate_code("abc")
    auth.refresh_from_db()
    rc = RecoveryCodes(auth)
    assert rc.generate_codes() == ["def"]
    assert rc.get_unused_codes() == ["def"]
    rc.validate_code("def")
    assert rc.instance.data["migrated_codes"] == []


def test_validate_code_on_stale_instance(user):
    rc = RecoveryCodes.activate(user)
    code = rc.generate_codes()[0]
    stale_rc = Authenticator.objects.get(pk=rc.instance.pk).wrap()
    assert rc.validate_code(code)
    assert not stale_rc.validate_code(code)


def test_validate_non_ascii_code(user):
    rc = RecoveryCodes.activate(user)
    assert not rc.validate_code("€#")
