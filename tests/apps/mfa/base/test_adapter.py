from unittest.mock import patch

from allauth.mfa.adapter import get_adapter


def test_build_totp_url_encodes_spaces_as_percent(user):
    """Spaces in the issuer name should be percent-encoded (%20), not encoded as
    '+', so that authenticator apps display the issuer correctly.
    """
    adapter = get_adapter()
    with patch.object(adapter, "get_totp_issuer", return_value="My Company"):
        url = adapter.build_totp_url(user, "JBSWY3DPEHPK3PXP")
    assert "issuer=My%20Company" in url
    assert "issuer=My+Company" not in url
