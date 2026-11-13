import pytest

from allauth.idp.oidc.adapter import DefaultOIDCAdapter


def test_scope_display_deprecation():
    with pytest.warns(DeprecationWarning, match=r"scope_display is deprecated"):

        class DeprecatedScopeDisplayAdapter(DefaultOIDCAdapter):
            scope_display = {
                **DefaultOIDCAdapter.scope_display,
                "custom": "Custom scope",
            }

    assert DeprecatedScopeDisplayAdapter.scope_display["custom"] == "Custom scope"
