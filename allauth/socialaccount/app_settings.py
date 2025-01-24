class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def QUERY_EMAIL(self):
        """
        Request email address from 3rd party account provider?
        E.g. using OpenID AX
        """
        from allauth.account import app_settings as account_settings

        return self._setting("QUERY_EMAIL", account_settings.EMAIL_REQUIRED)

    @property
    def AUTO_SIGNUP(self):
        """
        Attempt to bypass the signup form by using fields (e.g. username,
        email) retrieved from the social account provider. If a conflict
        arises due to a duplicate email signup form will still kick in.
        """
        return self._setting("AUTO_SIGNUP", True)

    @property
    def PROVIDERS(self):
        """
        Provider specific settings
        """
        ret = self._setting("PROVIDERS", {})
        oidc = ret.get("openid_connect")
        if oidc:
            ret["openid_connect"] = self._migrate_oidc(oidc)
        return ret

    def _migrate_oidc(self, oidc):
        servers = oidc.get("SERVERS")
        if servers is None:
            return oidc
        ret = {}
        apps = []
        for server in servers:
            app = dict(**server["APP"])
            app_settings = {}
            if "token_auth_method" in server:
                app_settings["token_auth_method"] = server["token_auth_method"]
            app_settings["server_url"] = server["server_url"]
            app.update(
                {
                    "name": server.get("name", ""),
                    "provider_id": server["id"],
                    "settings": app_settings,
                }
            )
            assert app["provider_id"]  # nosec
            apps.append(app)
        ret["APPS"] = apps
        return ret

    @property
    def EMAIL_REQUIRED(self):
        """
        The user is required to hand over an email address when signing up
        """
        from allauth.account import app_settings as account_settings

        return self._setting("EMAIL_REQUIRED", account_settings.EMAIL_REQUIRED)

    @property
    def EMAIL_VERIFICATION(self):
        """
        See email verification method.  When `None`, the default
        `allauth.account` logic kicks in.
        """
        from allauth import app_settings as allauth_settings
        from allauth.account import app_settings as account_settings

        dflt = (
            account_settings.EmailVerificationMethod.NONE
            if allauth_settings.SOCIALACCOUNT_ONLY
            else None
        )
        return self._setting("EMAIL_VERIFICATION", dflt)

    @property
    def EMAIL_AUTHENTICATION(self):
        """Consider a scenario where a social login occurs, and the social
        account comes with a verified email address (verified by the account
        provider), but that email address is already taken by a local user
        account. Additionally, assume that the local user account does not have
        any social account connected. Now, if the provider can be fully trusted,
        you can argue that we should treat this scenario as a login to the
        existing local user account even if the local account does not already
        have the social account connected, because -- according to the provider
        -- the user logging in has ownership of the email address.  This is how
        this scenario is handled when `EMAIL_AUTHENTICATION` is set to
        `True`. As this implies that an untrustworthy provider can login to any
        local account by fabricating social account data, this setting defaults
        to `False`. Only set it to `True` if you are using providers that can be
        fully trusted.
        """
        return self._setting("EMAIL_AUTHENTICATION", False)

    @property
    def EMAIL_AUTHENTICATION_AUTO_CONNECT(self):
        """In case email authentication is applied, this setting controls
        whether or not the social account is automatically connected to the
        local account. In case of ``False`` (the default) the local account
        remains unchanged during the login. In case of ``True``, the social
        account for which the email matched, is automatically added to the list
        of social accounts connected to the local account. As a result, even if
        the user were to change the email address afterwards, social login
        would still be possible when using ``True``, but not in case of
        ``False``.
        """
        return self._setting("EMAIL_AUTHENTICATION_AUTO_CONNECT", False)

    @property
    def ADAPTER(self):
        return self._setting(
            "ADAPTER",
            "allauth.socialaccount.adapter.DefaultSocialAccountAdapter",
        )

    @property
    def FORMS(self):
        return self._setting("FORMS", {})

    @property
    def LOGIN_ON_GET(self):
        return self._setting("LOGIN_ON_GET", False)

    @property
    def STORE_TOKENS(self):
        return self._setting("STORE_TOKENS", False)

    @property
    def UID_MAX_LENGTH(self):
        return 191

    @property
    def SOCIALACCOUNT_STR(self):
        return self._setting("SOCIALACCOUNT_STR", None)

    @property
    def REQUESTS_TIMEOUT(self):
        return self._setting("REQUESTS_TIMEOUT", 5)

    @property
    def OPENID_CONNECT_URL_PREFIX(self):
        return self._setting("OPENID_CONNECT_URL_PREFIX", "oidc")


_app_settings = AppSettings("SOCIALACCOUNT_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
