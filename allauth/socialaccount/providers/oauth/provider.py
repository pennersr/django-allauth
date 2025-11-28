import logging
from urllib.parse import parse_qsl

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.base.constants import AuthAction
from allauth.socialaccount.providers.oauth.client import OAuthError


logger = logging.getLogger(__name__)


class OAuthProvider(Provider):
    supports_redirect = True

    def get_login_url(self, request, **kwargs):
        url = reverse(f"{self.id}_login")
        if kwargs:
            url = f"{url}?{urlencode(kwargs)}"
        return url

    def get_auth_params(self):
        settings = self.get_settings()
        ret = dict(settings.get("AUTH_PARAMS", {}))
        return ret

    def get_auth_params_from_request(self, request, action):
        ret = self.get_auth_params()
        dynamic_auth_params = request.GET.get("auth_params", None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def get_auth_url(self, request, action):
        # TODO: This is ugly. Move authorization_url away from the
        # adapter into the provider. Hmpf, the line between
        # adapter/provider is a bit too thin here.
        return None

    def get_scope_from_request(self, request):
        return self.get_scope()

    def get_scope(self):
        settings = self.get_settings()
        scope = settings.get("SCOPE")
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_default_scope(self):
        return []

    def get_oauth_adapter(self, request):
        if not hasattr(self, "oauth_adapter_class"):
            raise ImproperlyConfigured(f"No oauth_adapter_class set for {self!r}")
        return self.oauth_adapter_class(request)

    def get_redirect_from_request_kwargs(self, request):
        kwargs = super().get_redirect_from_request_kwargs(request)
        kwargs["scope"] = self.get_scope_from_request(request)
        action = request.GET.get("action", AuthAction.AUTHENTICATE)
        kwargs["action"] = action
        kwargs["auth_params"] = self.get_auth_params_from_request(request, action)
        return kwargs

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        callback_url = reverse(f"{self.id}_callback")
        oauth_adapter = self.get_oauth_adapter(request)
        action = kwargs.pop("action", AuthAction.AUTHENTICATE)
        auth_url = self.get_auth_url(request, action) or oauth_adapter.authorize_url
        auth_params = kwargs.pop("auth_params", None)
        if auth_params is None:
            auth_params = self.get_auth_params()
        scope = kwargs.pop("scope", None)
        if scope is None:
            scope = self.get_scope()
        self.stash_redirect_state(request, process, next_url, data, **kwargs)
        client = oauth_adapter._get_client(request, callback_url, scope=scope)
        try:
            return client.get_redirect(auth_url, auth_params)
        except OAuthError as e:
            logger.error("OAuth authentication error", exc_info=True)
            return render_authentication_error(request, self, exception=e)
