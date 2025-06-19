from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.pinterest.provider import PinterestProvider


urlpatterns = default_urlpatterns(PinterestProvider)
