from django.urls import path

from allauth.headless.mfa import views


urlpatterns = [
    path(
        "v1/auth/mfa_authenticate",
        views.authenticate,
        name="headless_mfa_authenticate",
    ),
]
