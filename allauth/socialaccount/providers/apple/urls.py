from django.urls import path

from allauth.socialaccount.providers.apple.provider import AppleProvider
from allauth.socialaccount.providers.apple.views import oauth2_finish_login
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AppleProvider)
urlpatterns += [
    path(
        f"{AppleProvider.get_slug()}/login/callback/finish/",
        oauth2_finish_login,
        name="apple_finish_callback",
    ),
]
