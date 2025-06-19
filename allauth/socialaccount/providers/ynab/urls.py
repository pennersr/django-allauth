from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.ynab.provider import YNABProvider


urlpatterns = default_urlpatterns(YNABProvider)
