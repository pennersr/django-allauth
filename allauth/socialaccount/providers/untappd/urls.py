from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.untappd.provider import UntappdProvider


urlpatterns = default_urlpatterns(UntappdProvider)
