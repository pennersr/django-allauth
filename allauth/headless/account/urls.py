from django.urls import include, path

from allauth.headless.account import views


def build_urlpatterns(client):
    return [
        path("auth", views.AuthView.as_api_view(client=client), name="headless_auth"),
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
                                    views.RequestPasswordResetView.as_api_view(
                                        client=client
                                    ),
                                    name="headless_request_password_reset",
                                ),
                                path(
                                    "reset",
                                    views.ResetPasswordView.as_api_view(client=client),
                                    name="headless_reset_password",
                                ),
                            ]
                        ),
                    ),
                    path(
                        "login",
                        views.LoginView.as_api_view(client=client),
                        name="headless_login",
                    ),
                    path(
                        "reauthenticate",
                        views.ReauthenticateView.as_api_view(client=client),
                        name="headless_reauthenticate",
                    ),
                    path(
                        "logout",
                        views.LogoutView.as_api_view(client=client),
                        name="headless_logout",
                    ),
                    path(
                        "signup",
                        views.SignupView.as_api_view(client=client),
                        name="headless_signup",
                    ),
                    path(
                        "verify_email",
                        views.VerifyEmailView.as_api_view(client=client),
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
                        views.ChangePasswordView.as_api_view(client=client),
                        name="headless_change_password",
                    ),
                    path(
                        "email",
                        views.ManageEmailView.as_api_view(client=client),
                        name="headless_manage_email",
                    ),
                ]
            ),
        ),
    ]
