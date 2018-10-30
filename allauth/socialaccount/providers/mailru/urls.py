from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import MailRuProvider


urlpatterns = default_urlpatterns(MailRuProvider)
