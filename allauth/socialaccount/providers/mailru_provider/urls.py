from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import MailRuProvider


urlpatterns = default_urlpatterns(MailRuProvider)
