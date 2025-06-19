from django.urls import path

from allauth.socialaccount.providers.google import views
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GoogleProvider)

urlpatterns += [
    path(
        "google/login/token/",
        views.login_by_token,
        name="google_login_by_token",
    ),
]
