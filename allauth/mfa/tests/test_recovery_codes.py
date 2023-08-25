from allauth.mfa import app_settings
from allauth.mfa.recovery_codes import RecoveryCodes


def test_flow(user):
    rc = RecoveryCodes.activate(user)
    codes = rc.generate_codes()
    assert len(set(codes)) == app_settings.RECOVERY_CODE_COUNT
    for i in range(app_settings.RECOVERY_CODE_COUNT):
        assert not rc.is_code_used(i)
    idx = 3
    assert rc.validate_code(codes[idx])
    for i in range(app_settings.RECOVERY_CODE_COUNT):
        assert rc.is_code_used(i) == (i == idx)
    assert not rc.validate_code(codes[idx])

    unused_codes = rc.get_unused_codes()
    assert codes[idx] not in unused_codes
    assert len(unused_codes) == app_settings.RECOVERY_CODE_COUNT - 1
