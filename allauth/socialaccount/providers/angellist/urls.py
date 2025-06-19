from allauth.socialaccount.providers.angellist.provider import AngelListProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AngelListProvider)
