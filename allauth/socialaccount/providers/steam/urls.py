from django.conf.urls import url

from . import views


urlpatterns = [
    url("^steam/login/$", views.steam_login, name="steam_login"),
    url("^steam/callback/$", views.steam_callback, name="steam_callback"),
]
