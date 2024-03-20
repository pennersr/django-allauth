from django.urls import include, path

from allauth.headless.account import views


urlpatterns = [
    path("auth", views.auth, name="headless_auth"),
    path(
        "auth/",
        include(
            [
                path(
                    "password/",
                    include(
                        [
                            path(
                                "request",
                                views.request_password_reset,
                                name="headless_request_password_reset",
                            ),
                            path(
                                "reset",
                                views.reset_password,
                                name="headless_reset_password",
                            ),
                        ]
                    ),
                ),
                path(
                    "login",
                    views.login,
                    name="headless_login",
                ),
                path(
                    "reauthenticate",
                    views.reauthenticate,
                    name="headless_reauthenticate",
                ),
                path(
                    "logout",
                    views.logout,
                    name="headless_logout",
                ),
                path(
                    "signup",
                    views.signup,
                    name="headless_signup",
                ),
                path(
                    "verify_email",
                    views.verify_email,
                    name="headless_verify_email",
                ),
            ]
        ),
    ),
    path(
        "account/",
        include(
            [
                path(
                    "password/change",
                    views.change_password,
                    name="headless_change_password",
                ),
                path(
                    "email",
                    views.manage_email,
                    name="headless_manage_email",
                ),
            ]
        ),
    ),
]
