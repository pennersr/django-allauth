from django.urls import path

from . import views


urlpatterns = [
    path(
        "login/cancelled/",
        views.login_cancelled,
        name="socialaccount_login_cancelled",
    ),
    path("login/error/", views.login_error, name="socialaccount_login_error"),
    path("signup/", views.signup, name="socialaccount_signup"),
    path("", views.connections, name="socialaccount_connections"),
]
