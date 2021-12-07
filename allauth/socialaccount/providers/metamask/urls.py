from django.urls import path

from . import views

urlpatterns = [
    path("metamask/login_api/", views.login_api, name="login_api"),
]
