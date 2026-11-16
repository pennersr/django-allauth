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
                path(
                    "logout/",
                    views.logout,
                    name="openid_connect_logout",
                ),
                path(
                    "logout/callback/",
                    views.logout_callback,
                    name="openid_connect_logout_callback",
                ),
                path(
                    "logout/backchannel/",
                    views.backchannel_logout,
                    name="openid_connect_backchannel_logout",
                ),
            ]
        ),
    )
]

if app_settings.OPENID_CONNECT_URL_PREFIX:
    urlpatterns = [
        path(f"{app_settings.OPENID_CONNECT_URL_PREFIX}/", include(urlpatterns))
    ]
