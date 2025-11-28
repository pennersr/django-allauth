from typing import Type
from urllib.parse import parse_qsl

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.base.constants import AuthAction
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.utils import generate_code_challenge
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


class OAuth2Provider(Provider):
    pkce_enabled_default = False
    oauth2_adapter_class: Type[OAuth2Adapter]
    supports_redirect = True

    def get_login_url(self, request, **kwargs):
        url = reverse(f"{self.id}_login")
        if kwargs:
            url = f"{url}?{urlencode(kwargs)}"
        return url

    def get_callback_url(self):
        return reverse(f"{self.id}_callback")

    def get_pkce_params(self) -> dict:
        enabled = self.app.settings.get("oauth_pkce_enabled")
        if enabled is None:
            settings = self.get_settings()
            enabled = settings.get("OAUTH_PKCE_ENABLED", self.pkce_enabled_default)
        if enabled:
            pkce_code_params = generate_code_challenge()
            return pkce_code_params
        return {}

    def get_auth_params(self):
        """
        Returns a dictionary of additional parameters passed to the OAuth2
        redirect URL. Additional -- so no need to pass the standard `client_id`,
        `redirect_uri`, `response_type`.
        """
        ret = self.app.settings.get("auth_params")
        if ret is None:
            settings = self.get_settings()
            ret = settings.get("AUTH_PARAMS", {})
        return dict(ret)

    def get_auth_params_from_request(self, request, action):
        """
        Returns a dictionary of additional parameters passed to the OAuth2
        redirect URL. Additional -- so no need to pass the standard `client_id`,
        `redirect_uri`, `response_type`.
        """
        ret = self.get_auth_params()
        dynamic_auth_params = request.GET.get("auth_params", None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def get_default_scope(self):
        """
        Returns the default scope to use.
        """
        return []

    def get_scope(self):
        """
        Returns the scope to use, taking settings `SCOPE` into consideration.
        """
        scope = self.app.settings.get("scope")
        if scope is None:
            settings = self.get_settings()
            scope = settings.get("SCOPE", self.get_default_scope())
        return list(scope)

    def get_scope_from_request(self, request):
        """
        Returns the scope to use for the given request.
        """
        scope = self.get_scope()
        dynamic_scope = request.GET.get("scope", None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(","))
        return scope

    def get_oauth2_adapter(self, request):
        if not hasattr(self, "oauth2_adapter_class"):
            raise ImproperlyConfigured(f"No oauth2_adapter_class set for {self!r}")
        return self.oauth2_adapter_class(request)

    def get_redirect_from_request_kwargs(self, request):
        kwargs = super().get_redirect_from_request_kwargs(request)
        kwargs["scope"] = self.get_scope_from_request(request)
        action = request.GET.get("action", AuthAction.AUTHENTICATE)
        kwargs["auth_params"] = self.get_auth_params_from_request(request, action)
        return kwargs

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        app = self.app
        oauth2_adapter = self.get_oauth2_adapter(request)
        client = oauth2_adapter.get_client(request, app)

        auth_params = kwargs.pop("auth_params", None)
        if auth_params is None:
            auth_params = self.get_auth_params()
        pkce_params = self.get_pkce_params()
        code_verifier = pkce_params.pop("code_verifier", None)
        auth_params.update(pkce_params)

        scope = kwargs.pop("scope", None)
        if scope is None:
            scope = self.get_scope()

        state_id = self.stash_redirect_state(
            request, process, next_url, data, pkce_code_verifier=code_verifier, **kwargs
        )
        client.state = state_id
        try:
            return HttpResponseRedirect(
                client.get_redirect_url(
                    oauth2_adapter.authorize_url, scope, auth_params
                )
            )
        except OAuth2Error as e:
            return render_authentication_error(
                request, self, extra_context={"state_id": state_id}, exception=e
            )
