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
                        name="headless_mfa_authenticate",
                    ),
                    path(
                        "2fa/reauthenticate",
                        views.ReauthenticateView.as_api_view(client=client),
                        name="headless_mfa_reauthenticate",
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
                        name="headless_mfa_authenticators",
                    ),
                    path(
                        "authenticators/totp",
                        views.ManageTOTPView.as_api_view(client=client),
                        name="headless_mfa_manage_totp",
                    ),
                    path(
                        "authenticators/recovery_codes",
                        views.ManageRecoveryCodesView.as_api_view(client=client),
                        name="headless_mfa_manage_recovery_codes",
                    ),
                ]
            ),
        ),
    ]
