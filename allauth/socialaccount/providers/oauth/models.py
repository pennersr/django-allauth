from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider

class OAuthProvider(Provider):
    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url


