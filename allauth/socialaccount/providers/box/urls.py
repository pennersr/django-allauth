from allauth.socialaccount.providers.box.provider import BoxOAuth2Provider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BoxOAuth2Provider)
