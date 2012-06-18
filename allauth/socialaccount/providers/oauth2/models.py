from django.core.urlresolvers import reverse

from allauth.socialaccount.providers.base import Provider

class OAuth2Provider(Provider):
    def get_login_url(self, request, **kwargs):
        return reverse(self.id + "_login")


