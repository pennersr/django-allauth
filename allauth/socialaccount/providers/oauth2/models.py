from django.core.urlresolvers import reverse

from allauth.socialaccount.providers.base import Provider

class OAuth2Provider(Provider):
    def get_login_url(self, request, **kwargs):
        return reverse(self.id + "_login")

    def get_scope(self):
        settings = self.get_settings()
        scope = settings.get('SCOPE')
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_default_scope(self):
        return []


