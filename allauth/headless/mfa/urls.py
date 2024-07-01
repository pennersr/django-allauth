from django.urls import include, path

from allauth.headless.mfa import views
from allauth.mfa import app_settings as mfa_settings


def build_urlpatterns(client):
    authenticators = []
    if "totp" in mfa_settings.SUPPORTED_TYPES:
        authenticators.append(
            path(
                "totp",
                views.ManageTOTPView.as_api_view(client=client),
                name="manage_totp",
            )
        )
    if "recovery_codes" in mfa_settings.SUPPORTED_TYPES:
        authenticators.append(
            path(
                "recovery-codes",
                views.ManageRecoveryCodesView.as_api_view(client=client),
                name="manage_recovery_codes",
            )
        )
    if "webauthn" in mfa_settings.SUPPORTED_TYPES:
        authenticators.append(
            path(
                "webauthn",
                views.ManageWebAuthnView.as_api_view(client=client),
                name="manage_webauthn",
            )
        )
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
                        "authenticators/",
                        include(authenticators),
                    ),
                ]
            ),
        ),
    ]
