from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path

from allauth.mfa import app_settings


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("", include("allauth.mfa.base.urls"))
]

if "totp" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(path("totp/", include("allauth.mfa.totp.urls")))

if "recovery_codes" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(
        path("recovery-codes/", include("allauth.mfa.recovery_codes.urls"))
    )

if "webauthn" in app_settings.SUPPORTED_TYPES:
    urlpatterns.append(path("webauthn/", include("allauth.mfa.webauthn.urls")))
