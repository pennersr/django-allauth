from django.urls import include, path

from allauth.account import app_settings as account_settings
from allauth.headless.account import views


def build_urlpatterns(client):
    return [
        path(
            "auth/",
            include(
                [
                    path(
                        "session",
                        views.SessionView.as_api_view(client=client),
                        name="current_session",
                    ),
                    path(
                        "password/",
                        include(
                            [
                                path(
                                    "request",
                                    views.RequestPasswordResetView.as_api_view(
                                        client=client
                                    ),
                                    name="request_password_reset",
                                ),
                                path(
                                    "reset",
                                    views.ResetPasswordView.as_api_view(client=client),
                                    name="reset_password",
                                ),
                            ]
                        ),
                    ),
                    path(
                        "login",
                        views.LoginView.as_api_view(client=client),
                        name="login",
                    ),
                    path(
                        "reauthenticate",
                        views.ReauthenticateView.as_api_view(client=client),
                        name="reauthenticate",
                    ),
                    path(
                        "signup",
                        views.SignupView.as_api_view(client=client),
                        name="signup",
                    ),
                    path(
                        "email/verify",
                        views.VerifyEmailView.as_api_view(client=client),
                        name="verify_email",
                    ),
                ]
                + (
                    [
                        path(
                            "code/request",
                            views.RequestLoginCodeView.as_api_view(client=client),
                            name="request_login_code",
                        ),
                        path(
                            "code/confirm",
                            views.ConfirmLoginCodeView.as_api_view(client=client),
                            name="confirm_login_code",
                        ),
                    ]
                    if account_settings.LOGIN_BY_CODE_ENABLED
                    else []
                )
            ),
        ),
        path(
            "account/",
            include(
                [
                    path(
                        "password/change",
                        views.ChangePasswordView.as_api_view(client=client),
                        name="change_password",
                    ),
                    path(
                        "email",
                        views.ManageEmailView.as_api_view(client=client),
                        name="manage_email",
                    ),
                ]
            ),
        ),
    ]
