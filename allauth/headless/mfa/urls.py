from django.urls import include, path

from allauth.headless.mfa import views


urlpatterns = [
    path(
        "auth/",
        include(
            [
                path(
                    "2fa/authenticate",
                    views.authenticate,
                    name="headless_mfa_authenticate",
                ),
                path(
                    "2fa/reauthenticate",
                    views.reauthenticate,
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
                    "2fa/",
                    include(
                        [
                            path(
                                "authenticators",
                                views.authenticators,
                                name="headless_mfa_authenticators",
                            ),
                            path(
                                "authenticators/totp",
                                views.manage_totp,
                                name="headless_mfa_manage_totp",
                            ),
                            path(
                                "authenticators/recovery_codes",
                                views.manage_recovery_codes,
                                name="headless_mfa_manage_recovery_codes",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
