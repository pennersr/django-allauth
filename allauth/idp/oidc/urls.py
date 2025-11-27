from django.urls import include, path

from allauth.idp.oidc import app_settings, views


app_name = "oidc"


_api_urlpatterns = [
    path(
        "token",
        views.token,
        name="token",
    ),
    path(
        "revoke",
        views.revoke,
        name="revoke",
    ),
    path(
        "device/code",
        views.device_code,
        name="device_code",
    ),
]

if not app_settings.USERINFO_ENDPOINT:
    _api_urlpatterns.append(
        path(
            "userinfo",
            views.user_info,
            name="userinfo",
        )
    )


urlpatterns = [
    path(
        ".well-known/",
        include(
            [
                path(
                    "openid-configuration",
                    views.configuration,
                    name="configuration",
                ),
                path(
                    "jwks.json",
                    views.jwks,
                    name="jwks",
                ),
            ]
        ),
    ),
    path(
        "identity/",
        include(
            [
                path(
                    "o/",
                    include(
                        [
                            path(
                                "authorize",
                                views.authorization,
                                name="authorization",
                            ),
                            path(
                                "device",
                                views.device_authorization,
                                name="device_authorization",
                            ),
                            path(
                                "logout",
                                views.logout,
                                name="logout",
                            ),
                            path("api/", include(_api_urlpatterns)),
                        ]
                    ),
                )
            ]
        ),
    ),
]
