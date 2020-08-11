from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FigmaProvider


urlpatterns = default_urlpatterns(FigmaProvider)
