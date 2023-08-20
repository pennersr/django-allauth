from django.urls import include, path

from allauth.mfa import views


urlpatterns = [
    path("", views.index, name="mfa_index"),
    path("authenticate/", views.authenticate, name="mfa_authenticate"),
    path(
        "totp/",
        include(
            [
                path("activate/", views.activate_totp, name="mfa_activate_totp"),
                path("deactivate/", views.deactivate_totp, name="mfa_deactivate_totp"),
            ]
        ),
    ),
]
