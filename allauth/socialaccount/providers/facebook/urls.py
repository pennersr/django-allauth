from django.urls import path

from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from . import views


urlpatterns = default_urlpatterns(FacebookProvider)

urlpatterns += [
    path(
        "facebook/login/token/",
        views.login_by_token,
        name="facebook_login_by_token",
    ),
]
