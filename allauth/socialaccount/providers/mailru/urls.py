from allauth.socialaccount.providers.mailru.provider import MailRuProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MailRuProvider)
