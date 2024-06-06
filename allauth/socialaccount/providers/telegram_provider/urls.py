from django.urls import path

from . import views


urlpatterns = [
    path("telegram/login/", views.login, name="telegram_login"),
    path("telegram/login/callback/", views.callback, name="telegram_callback"),
]
