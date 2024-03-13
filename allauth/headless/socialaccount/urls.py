from django.urls import path

from allauth.headless.socialaccount import views


urlpatterns = [
    path(
        "v1/account/providers",
        views.manage_providers,
        name="headless_manage_providers",
    ),
    path(
        "v1/auth/provider/signup",
        views.provider_signup,
        name="headless_provider_signup",
    ),
    path(
        "v1/auth/provider/redirect",
        views.redirect_to_provider,
        name="headless_redirect_to_provider",
    ),
]
