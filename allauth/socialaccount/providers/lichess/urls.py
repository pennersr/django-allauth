from allauth.socialaccount.providers.lichess.provider import LichessProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LichessProvider)
