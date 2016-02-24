from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import UntappdProvider

urlpatterns = default_urlpatterns(UntappdProvider)
