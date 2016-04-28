from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import EveOnlineProvider

urlpatterns = default_urlpatterns(EveOnlineProvider)
