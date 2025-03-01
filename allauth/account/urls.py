from django.conf import settings
from django.urls import path, re_path

from allauth import app_settings as allauth_app_settings
from allauth.account import app_settings

from . import views


urlpatterns = [
    path("login/", views.login, name="account_login"),
    path("logout/", views.logout, name="account_logout"),
    path("inactive/", views.account_inactive, name="account_inactive"),
]

if not allauth_app_settings.SOCIALACCOUNT_ONLY:
    urlpatterns.extend(
        [
            path("signup/", views.signup, name="account_signup"),
            path(
                "reauthenticate/", views.reauthenticate, name="account_reauthenticate"
            ),
            # Email
            path("email/", views.email, name="account_email"),
            path(
                "confirm-email/",
                views.email_verification_sent,
                name="account_email_verification_sent",
            ),
            re_path(
                r"^confirm-email/(?P<key>[-:\w]+)/$",
                views.confirm_email,
                name="account_confirm_email",
            ),
            path(
                "password/change/",
                views.password_change,
                name="account_change_password",
            ),
            path("password/set/", views.password_set, name="account_set_password"),
            # password reset
            path(
                "password/reset/", views.password_reset, name="account_reset_password"
            ),
            path(
                "login/code/confirm/",
                views.confirm_login_code,
                name="account_confirm_login_code",
            ),
        ]
    )
    if "phone" in app_settings.SIGNUP_FIELDS:
        urlpatterns.extend(
            [
                path(
                    "phone/verify/",
                    views.verify_phone,
                    name="account_verify_phone",
                ),
                path(
                    "phone/change/",
                    views.change_phone,
                    name="account_change_phone",
                ),
            ]
        )
    if app_settings.PASSWORD_RESET_BY_CODE_ENABLED:
        urlpatterns.extend(
            [
                path(
                    "password/reset/confirm/",
                    views.confirm_password_reset_code,
                    name="account_confirm_password_reset_code",
                ),
                path(
                    "password/reset/complete/",
                    views.complete_password_reset,
                    name="account_complete_password_reset",
                ),
                path(
                    "password/reset/done/",
                    views.password_reset_from_key_done,
                    name="account_password_reset_completed",
                ),
            ]
        )
    else:
        urlpatterns.extend(
            [
                path(
                    "password/reset/key/done/",
                    views.password_reset_from_key_done,
                    name="account_reset_password_from_key_done",
                ),
                re_path(
                    r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
                    views.password_reset_from_key,
                    name="account_reset_password_from_key",
                ),
                path(
                    "password/reset/done/",
                    views.password_reset_done,
                    name="account_reset_password_done",
                ),
            ]
        )
    if getattr(settings, "MFA_PASSKEY_SIGNUP_ENABLED", False):
        urlpatterns.append(
            path(
                "signup/passkey/",
                views.signup_by_passkey,
                name="account_signup_by_passkey",
            )
        )

if app_settings.LOGIN_BY_CODE_ENABLED:
    urlpatterns.extend(
        [
            path(
                "login/code/",
                views.request_login_code,
                name="account_request_login_code",
            ),
        ]
    )
