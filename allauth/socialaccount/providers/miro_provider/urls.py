from allauth.socialaccount.providers.miro_provider.provider import MiroProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MiroProvider)
