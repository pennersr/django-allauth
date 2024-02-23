from django.urls import path

from allauth.headless.account import views


urlpatterns = [
    path(
        "v1/auth/password/request",
        views.request_password_reset,
        name="headless_request_password_reset",
    ),
    path(
        "v1/auth/password/reset",
        views.reset_password,
        name="headless_reset_password",
    ),
    path(
        "v1/account/password/change",
        views.change_password,
        name="headless_change_password",
    ),
    path(
        "v1/account/email",
        views.manage_email,
        name="headless_manage_email",
    ),
    path("v1/auth/login", views.login, name="headless_login"),
    path("v1/auth/logout", views.logout, name="headless_logout"),
    path("v1/auth/signup", views.signup, name="headless_signup"),
    path("v1/auth/verify_email", views.verify_email, name="headless_verify_email"),
    path("v1/auth", views.auth, name="headless_auth"),
]
