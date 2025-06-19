from allauth.socialaccount.providers.eveonline.provider import EveOnlineProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EveOnlineProvider)
