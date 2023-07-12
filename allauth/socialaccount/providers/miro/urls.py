from allauth.socialaccount.providers.miro.provider import MiroProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MiroProvider)
