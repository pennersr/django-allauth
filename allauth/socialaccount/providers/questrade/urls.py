from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.questrade.provider import QuestradeProvider


urlpatterns = default_urlpatterns(QuestradeProvider)
