from django.urls import path

from allauth.headless.mfa import views


urlpatterns = [
    path(
        "v1/auth/mfa_authenticate",
        views.authenticate,
        name="headless_mfa_authenticate",
    ),
    path(
        "v1/2fa/authenticators",
        views.authenticators,
        name="headless_mfa_authenticators",
    ),
    path(
        "v1/2fa/authenticators/totp",
        views.manage_totp,
        name="headless_mfa_manage_totp",
    ),
    path(
        "v1/2fa/authenticators/recovery_codes",
        views.manage_recovery_codes,
        name="headless_mfa_manage_recovery_codes",
    ),
]
