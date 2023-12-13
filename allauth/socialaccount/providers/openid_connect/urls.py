from django.urls import include, path, re_path

from allauth.socialaccount import app_settings

from . import views


urlpatterns = [
    re_path(
        r"^(?P<provider_id>[^/]+)/",
        include(
            [
                path(
                    "login/",
                    views.login,
                    name="openid_connect_login",
                ),
                path(
                    "login/callback/",
                    views.callback,
                    name="openid_connect_callback",
                ),
            ]
        ),
    )
]

if app_settings.OPENID_CONNECT_URL_PREFIX:
    urlpatterns = [
        path(f"{app_settings.OPENID_CONNECT_URL_PREFIX}/", include(urlpatterns))
    ]
