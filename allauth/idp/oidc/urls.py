from django.urls import include, path

from allauth.idp.oidc import views


app_name = "oidc"
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
                                "api/",
                                include(
                                    [
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
                                            "userinfo",
                                            views.user_info,
                                            name="userinfo",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                )
            ]
        ),
    ),
]
