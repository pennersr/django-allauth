from django.urls import path

from . import views


urlpatterns = [
    path("dummy/login/", views.login, name="dummy_login"),
    path("dummy/authenticate/", views.authenticate, name="dummy_authenticate"),
]
