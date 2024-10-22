import requests
import string
from urllib.parse import quote

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.html import escapejs

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import (
    AuthAction,
    AuthProcess,
    ProviderAccount,
)
from allauth.socialaccount.providers.facebook.constants import (
    GRAPH_API_URL,
    GRAPH_API_VERSION,
    NONCE_LENGTH,
    NONCE_SESSION_KEY,
    PROVIDER_ID,
)
from allauth.socialaccount.providers.facebook.views import (
    FacebookOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.utils import import_callable

from .locale import get_default_locale_callable


class FacebookAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("link")

    def get_avatar_url(self):
        uid = self.account.uid
        # ask for a 600x600 pixel image. We might get smaller but
        # image will always be highest res possible and square
        return (
            GRAPH_API_URL
            + "/%s/picture?type=square&height=600&width=600&return_ssl_resources=1"
            % uid
        )  # noqa


class FacebookProvider(OAuth2Provider):
    id = PROVIDER_ID
    name = "Facebook"
    account_class = FacebookAccount
    oauth2_adapter_class = FacebookOAuth2Adapter
    supports_token_authentication = True

    # TODO: populate these from https://www.facebook.com/.well-known/openid-configuration/
    #  just like in a normal OIDC provider (as that's what "Limited Login" really is)
    limited_login_expected_jwt_issuer = "https://www.facebook.com"
    limited_login_jwks_url = (
        "https://limited.facebook.com/.well-known/oauth/openid/jwks/"
    )

    def __init__(self, *args, **kwargs):
        self._locale_callable_cache = None
        super().__init__(*args, **kwargs)

    def get_method(self):
        return self.get_settings().get("METHOD", "oauth2")

    def get_login_url(self, request, **kwargs):
        method = kwargs.pop("method", self.get_method())
        if method == "js_sdk":
            next = "'%s'" % escapejs(kwargs.get(REDIRECT_FIELD_NAME) or "")
            process = "'%s'" % escapejs(kwargs.get("process") or AuthProcess.LOGIN)
            action = "'%s'" % escapejs(kwargs.get("action") or AuthAction.AUTHENTICATE)
            scope = "'%s'" % escapejs(kwargs.get("scope", ""))
            js = "allauth.facebook.login(%s, %s, %s, %s)" % (
                next,
                action,
                process,
                scope,
            )
            ret = "javascript:%s" % (quote(js),)
        elif method == "oauth2":
            ret = super(FacebookProvider, self).get_login_url(request, **kwargs)
        else:
            raise RuntimeError("Invalid method specified: %s" % method)
        return ret

    def _get_locale_callable(self):
        settings = self.get_settings()
        func = settings.get("LOCALE_FUNC")
        return import_callable(func) if func else get_default_locale_callable()

    def get_locale_for_request(self, request):
        if not self._locale_callable_cache:
            self._locale_callable_cache = self._get_locale_callable()
        return self._locale_callable_cache(request)

    def get_default_scope(self):
        scope = []
        if QUERY_EMAIL:
            scope.append("email")
        return scope

    def get_fields(self):
        settings = self.get_settings()
        default_fields = [
            "id",
            "email",
            "name",
            "first_name",
            "last_name",
            "verified",
            "locale",
            "timezone",
            "link",
            "gender",
            "updated_time",
        ]
        return settings.get("FIELDS", default_fields)

    def get_auth_params_from_request(self, request, action):
        ret = super().get_auth_params_from_request(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret["auth_type"] = "reauthenticate"
        elif action == AuthAction.REREQUEST:
            ret["auth_type"] = "rerequest"
        return ret

    def get_init_params(self, request, app):
        init_params = {"appId": app.client_id, "version": GRAPH_API_VERSION}
        settings = self.get_settings()
        init_params.update(settings.get("INIT_PARAMS", {}))
        return init_params

    def get_fb_login_options(self, request):
        ret = self.get_auth_params_from_request(request, "authenticate")
        ret["scope"] = ",".join(self.get_scope_from_request(request))
        if ret.get("auth_type") == "reauthenticate":
            ret["auth_nonce"] = self.get_nonce(request, or_create=True)
        return ret

    def get_sdk_url(self, request):
        settings = self.get_settings()
        sdk_url = settings.get("SDK_URL", "//connect.facebook.net/{locale}/sdk.js")
        field_names = [
            tup[1] for tup in string.Formatter().parse(sdk_url) if tup[1] is not None
        ]
        if "locale" in field_names:
            locale = self.get_locale_for_request(request)
            sdk_url = sdk_url.format(locale=locale)
        return sdk_url

    def media_js(self, request):
        if self.get_method() != "js_sdk":
            return ""

        def abs_uri(name):
            return request.build_absolute_uri(reverse(name))

        fb_data = {
            "appId": self.app.client_id,
            "version": GRAPH_API_VERSION,
            "sdkUrl": self.get_sdk_url(request),
            "initParams": self.get_init_params(request, self.app),
            "loginOptions": self.get_fb_login_options(request),
            "loginByTokenUrl": abs_uri("facebook_login_by_token"),
            "cancelUrl": abs_uri("socialaccount_login_cancelled"),
            "logoutUrl": abs_uri("account_logout"),
            "loginUrl": request.build_absolute_uri(
                self.get_login_url(request, method="oauth2")
            ),
            "errorUrl": abs_uri("socialaccount_login_error"),
            "csrfToken": get_token(request),
        }
        ctx = {"fb_data": fb_data}
        return render_to_string("facebook/fbconnect.html", ctx, request=request)

    def get_nonce(self, request, or_create=False, pop=False):
        if pop:
            nonce = request.session.pop(NONCE_SESSION_KEY, None)
        else:
            nonce = request.session.get(NONCE_SESSION_KEY)
        if not nonce and or_create:
            nonce = get_random_string(NONCE_LENGTH)
            request.session[NONCE_SESSION_KEY] = nonce
        return nonce

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            name=data.get("name"),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            # data['verified'] does not imply the email address is
            # verified.
            ret.append(EmailAddress(email=email, verified=False, primary=True))
        return ret

    def verify_token(self, request, token: dict):
        """
        Verifies both normal oAuth2-style "access_token"s as well
        as OIDC-style "Limited Login" JWTs.

        Limited Login is an OIDC-based form of Facebook Login
        that their iOS SDK uses when App Tracking Transparency consent is denied.
        """
        from allauth.socialaccount.providers.facebook import flows

        access_token = token.get("access_token")
        id_token = token.get("id_token")

        if not any([access_token, id_token]):
            raise get_adapter().validation_error("invalid_token")

        try:
            if access_token:
                return flows.verify_token(request, self, access_token)
            else:
                assert id_token
                return flows.verify_limited_login_token(request, self, id_token)
        except (OAuth2Error, requests.RequestException) as e:
            raise get_adapter().validation_error("invalid_token") from e


provider_classes = [FacebookProvider]
