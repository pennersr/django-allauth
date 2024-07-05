from django.urls import include, path

from allauth.headless.mfa import views
from allauth.mfa import app_settings as mfa_settings


def build_urlpatterns(client):
    auth_patterns = [
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
        authenticators.extend(
            [
                path(
                    "webauthn",
                    views.ManageWebAuthnView.as_api_view(client=client),
                    name="manage_webauthn",
                ),
            ]
        )
        auth_patterns.extend(
            [
                path(
                    "webauthn/authenticate",
                    views.AuthenticateWebAuthnView.as_api_view(client=client),
                    name="authenticate_webauthn",
                ),
                path(
                    "webauthn/reauthenticate",
                    views.ReauthenticateWebAuthnView.as_api_view(client=client),
                    name="reauthenticate_webauthn",
                ),
            ]
        )
        if mfa_settings.PASSKEY_LOGIN_ENABLED:
            auth_patterns.append(
                path(
                    "webauthn/login",
                    views.LoginWebAuthnView.as_api_view(client=client),
                    name="login_webauthn",
                )
            )

    return [
        path(
            "auth/",
            include(auth_patterns),
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
