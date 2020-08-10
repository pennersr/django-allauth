from django.urls import path

from . import views

urlpatterns = [
    path("rapidconnect/login/", views.login, name="rapidconnect_login"),
    path("rapidconnect/login/callback/", views.callback, name="rapidconnect_callback"),
]
