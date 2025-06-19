from allauth.socialaccount.providers.figma.provider import FigmaProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FigmaProvider)
