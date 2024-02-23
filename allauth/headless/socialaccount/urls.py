from django.urls import path

from allauth.headless.socialaccount import views


urlpatterns = [
    path(
        "v1/auth/provider_login",
        views.provider_login,
        name="headless_provider_login",
    ),
]
