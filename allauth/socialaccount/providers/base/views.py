from django.http import Http404
from django.views import View

from allauth import app_settings as allauth_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.base.utils import respond_to_login_on_get


class BaseLoginView(View):
    provider_id: str  # Set in subclasses

    def dispatch(self, request, *args, **kwargs):
        if allauth_settings.HEADLESS_ONLY:
            raise Http404
        provider = self.get_provider()
        resp = respond_to_login_on_get(request, provider)
        if resp:
            return resp
        return provider.redirect_from_request(request)

    def get_provider(self):
        provider = get_adapter().get_provider(self.request, self.provider_id)
        return provider
