from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path

from allauth.mfa import app_settings, views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("authenticate/", views.authenticate, name="mfa_authenticate"),
    path("reauthenticate/", views.reauthenticate, name="mfa_reauthenticate"),
]
if app_settings.PASSKEY_LOGIN_ENABLED:
    urlpatterns.append(path("login/", views.login, name="mfa_login"))

if app_settings.SUPPORTED_TYPES:
    urlpatterns.append(path("", views.index, name="mfa_index"))

if "totp" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(
        path(
            "totp/",
            include(
                [
                    path("activate/", views.activate_totp, name="mfa_activate_totp"),
                    path(
                        "deactivate/", views.deactivate_totp, name="mfa_deactivate_totp"
                    ),
                ]
            ),
        )
    )

if "recovery_codes" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(
        path(
            "recovery-codes/",
            include(
                [
                    path("", views.view_recovery_codes, name="mfa_view_recovery_codes"),
                    path(
                        "generate/",
                        views.generate_recovery_codes,
                        name="mfa_generate_recovery_codes",
                    ),
                    path(
                        "download/",
                        views.download_recovery_codes,
                        name="mfa_download_recovery_codes",
                    ),
                ]
            ),
        )
    )

if "webauthn" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(
        path(
            "webauthn/",
            include(
                [
                    path("", views.list_webauthn, name="mfa_list_webauthn"),
                    path("add/", views.add_webauthn, name="mfa_add_webauthn"),
                    path(
                        "reauthenticate/",
                        views.reauthenticate_webauthn,
                        name="mfa_reauthenticate_webauthn",
                    ),
                    path(
                        "<int:pk>/",
                        include(
                            [
                                path(
                                    "remove/",
                                    views.remove_webauthn,
                                    name="mfa_remove_webauthn",
                                ),
                                path(
                                    "edit/",
                                    views.edit_webauthn,
                                    name="mfa_edit_webauthn",
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        )
    )
