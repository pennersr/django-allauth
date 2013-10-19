from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider


class OAuthProvider(Provider):
    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url

    def get_auth_url(self, request, action):
        # TODO: This is ugly. Move authorization_url away from the
        # adapter into the provider. Hmpf, the line between
        # adapter/provider is a bit too thin here.
        return None

    def get_scope(self):
        settings = self.get_settings()
        scope = settings.get('SCOPE')
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_default_scope(self):
        return []
