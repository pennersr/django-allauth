import json
import string
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.html import escapejs, mark_safe

from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import (
    AuthAction,
    AuthProcess,
    ProviderAccount,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.utils import import_callable

from .locale import get_default_locale_callable


GRAPH_API_VERSION = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("facebook", {})
    .get("VERSION", "v7.0")
)
GRAPH_API_URL = "https://graph.facebook.com/" + GRAPH_API_VERSION

NONCE_SESSION_KEY = "allauth_facebook_nonce"
NONCE_LENGTH = 32


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

    def to_str(self):
        dflt = super(FacebookAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class FacebookProvider(OAuth2Provider):
    id = "facebook"
    name = "Facebook"
    account_class = FacebookAccount

    def __init__(self, request):
        self._locale_callable_cache = None
        super(FacebookProvider, self).__init__(request)

    def get_method(self):
        return self.get_settings().get("METHOD", "oauth2")

    def get_login_url(self, request, **kwargs):
        method = kwargs.pop("method", self.get_method())
        if method == "js_sdk":
            next = "'%s'" % escapejs(kwargs.get("next") or "")
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

    def get_auth_params(self, request, action):
        ret = super(FacebookProvider, self).get_auth_params(request, action)
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
        ret = self.get_auth_params(request, "authenticate")
        ret["scope"] = ",".join(self.get_scope(request))
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
        # NOTE: Avoid loading models at top due to registry boot...
        from allauth.socialaccount.models import SocialApp

        try:
            app = self.get_app(request)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured(
                "No Facebook app configured: please"
                " add a SocialApp using the Django"
                " admin"
            )

        def abs_uri(name):
            return request.build_absolute_uri(reverse(name))

        fb_data = {
            "appId": app.client_id,
            "version": GRAPH_API_VERSION,
            "sdkUrl": self.get_sdk_url(request),
            "initParams": self.get_init_params(request, app),
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
        ctx = {"fb_data": mark_safe(json.dumps(fb_data))}
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


provider_classes = [FacebookProvider]
