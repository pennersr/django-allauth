from django.urls import include, path, re_path

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
