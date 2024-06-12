from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path

from allauth.mfa import app_settings, views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("authenticate/", views.authenticate, name="mfa_authenticate"),
    path("reauthenticate/", views.reauthenticate, name="mfa_reauthenticate"),
]

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
        ),
    )
