import warnings
from urllib.parse import parse_qsl

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.base.constants import AuthAction
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.utils import (
    generate_code_challenge,
)


class OAuth2Provider(Provider):
    pkce_enabled_default = False
    oauth2_adapter_class = None
    supports_redirect = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.oauth2_adapter_class is None:
            warnings.warn("provider.oauth2_adapter_class property missing")

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def get_callback_url(self):
        return reverse(self.id + "_callback")

    def get_pkce_params(self):
        settings = self.get_settings()
        if settings.get("OAUTH_PKCE_ENABLED", self.pkce_enabled_default):
            pkce_code_params = generate_code_challenge()
            return pkce_code_params
        return {}

    def get_auth_params(self, request, action):
        """
        Returns a dictionary of additional parameters passed to the OAuth2
        redirect URL. Additional -- so no need to pass the standard `client_id`,
        `redirect_uri`, `response_type`.
        """
        settings = self.get_settings()
        ret = dict(settings.get("AUTH_PARAMS", {}))
        dynamic_auth_params = request.GET.get("auth_params", None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def get_scope(self, request):
        settings = self.get_settings()
        scope = list(settings.get("SCOPE", self.get_default_scope()))
        dynamic_scope = request.GET.get("scope", None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(","))
        return scope

    def get_default_scope(self):
        return []

    def get_oauth2_adapter(self, request):
        return self.oauth2_adapter_class(request)

    def get_redirect_from_request_kwargs(self, request):
        kwargs = super().get_redirect_from_request_kwargs(request)
        kwargs["scope"] = self.get_scope(request)
        action = request.GET.get("action", AuthAction.AUTHENTICATE)
        kwargs["auth_params"] = self.get_auth_params(request, action)
        return kwargs

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        app = self.app
        oauth2_adapter = self.get_oauth2_adapter(request)
        client = oauth2_adapter.get_client(request, app)
        auth_url = oauth2_adapter.authorize_url
        auth_params = kwargs["auth_params"]
        pkce_params = self.get_pkce_params()
        code_verifier = pkce_params.pop("code_verifier", None)
        auth_params.update(pkce_params)
        if code_verifier:
            request.session["pkce_code_verifier"] = code_verifier

        client.state = self.stash_redirect_state(request, process, next_url, data)
        scope = kwargs["scope"]
        try:
            return HttpResponseRedirect(
                client.get_redirect_url(auth_url, scope, auth_params)
            )
        except OAuth2Error as e:
            return render_authentication_error(request, self, exception=e)
