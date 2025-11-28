from typing import Optional


class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(f"{self.prefix}{name}", dflt)

    @property
    def ADAPTER(self):
        return self._setting(
            "ADAPTER",
            "allauth.idp.oidc.adapter.DefaultOIDCAdapter",
        )

    @property
    def ID_TOKEN_EXPIRES_IN(self) -> int:
        return 5 * 60

    @property
    def PRIVATE_KEY(self) -> str:
        return self._setting("PRIVATE_KEY", "")

    @property
    def ACCESS_TOKEN_EXPIRES_IN(self) -> int:
        return self._setting("ACCESS_TOKEN_EXPIRES_IN", 3600)

    @property
    def ACCESS_TOKEN_FORMAT(self) -> str:
        return self._setting("ACCESS_TOKEN_FORMAT", "opaque")

    @property
    def AUTHORIZATION_CODE_EXPIRES_IN(self) -> int:
        return self._setting("AUTHORIZATION_CODE_EXPIRES_IN", 60)

    @property
    def ROTATE_REFRESH_TOKEN(self) -> bool:
        return self._setting("ROTATE_REFRESH_TOKEN", True)

    @property
    def DEVICE_CODE_EXPIRES_IN(self) -> int:
        return self._setting("DEVICE_CODE_EXPIRES_IN", 300)

    @property
    def DEVICE_CODE_INTERVAL(self) -> int:
        return self._setting("DEVICE_CODE_INTERVAL", 5)

    @property
    def RATE_LIMITS(self):
        rls = self._setting("RATE_LIMITS", {})
        if rls is False:
            return {}
        ret = {
            # OIDC device user code checks
            "device_user_code": "5/m/ip"
        }
        ret.update(rls)
        return ret

    @property
    def RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT(self):
        """
        At https://openid.net/specs/openid-connect-rpinitiated-1_0.html

        > 2. RP-Initiated Logout':
        > At the Logout Endpoint, the OP SHOULD ask the End-User whether to
        > log out of the OP as well.

        This setting controls whether the OP always asks.
        """
        return self._setting("RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT", True)

    @property
    def USERINFO_ENDPOINT(self) -> Optional[str]:
        """
        This setting can be used to point the ``userinfo_endpoint`` value as
        returned in the ".well-known/openid-configuration" to a custom URL.
        Setting this disables the built-in userinfo endpoint.
        """
        return self._setting("USERINFO_ENDPOINT", None)


_app_settings = AppSettings("IDP_OIDC_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
