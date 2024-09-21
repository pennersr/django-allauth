from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path

from allauth.mfa import app_settings
from allauth.mfa.webauthn import views


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("", views.list_webauthn, name="mfa_list_webauthn"),
    path("add/", views.add_webauthn, name="mfa_add_webauthn"),
    path(
        "reauthenticate/",
        views.reauthenticate_webauthn,
        name="mfa_reauthenticate_webauthn",
    ),
    path(
        "keys/<int:pk>/",
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

if app_settings.PASSKEY_LOGIN_ENABLED:
    urlpatterns.append(path("login/", views.login_webauthn, name="mfa_login_webauthn"))
if app_settings.PASSKEY_SIGNUP_ENABLED:
    urlpatterns.append(
        path("signup/", views.signup_webauthn, name="mfa_signup_webauthn")
    )
