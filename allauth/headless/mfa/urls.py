from django.urls import include, path

from allauth.headless.mfa import views


def build_urlpatterns(client):
    return [
        path(
            "auth/",
            include(
                [
                    path(
                        "2fa/authenticate",
                        views.AuthenticateView.as_api_view(client=client),
                        name="authenticate",
                    ),
                    path(
                        "2fa/reauthenticate",
                        views.ReauthenticateView.as_api_view(client=client),
                        name="reauthenticate",
                    ),
                ]
            ),
        ),
        path(
            "account/",
            include(
                [
                    path(
                        "authenticators",
                        views.AuthenticatorsView.as_api_view(client=client),
                        name="authenticators",
                    ),
                    path(
                        "authenticators/totp",
                        views.ManageTOTPView.as_api_view(client=client),
                        name="manage_totp",
                    ),
                    path(
                        "authenticators/recovery-codes",
                        views.ManageRecoveryCodesView.as_api_view(client=client),
                        name="manage_recovery_codes",
                    ),
                ]
            ),
        ),
    ]
