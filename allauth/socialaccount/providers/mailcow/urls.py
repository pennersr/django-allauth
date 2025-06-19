from allauth.socialaccount.providers.mailcow.provider import MailcowProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MailcowProvider)
