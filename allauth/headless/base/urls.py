from django.urls import path

from allauth.headless.base import views


urlpatterns = [
    path("client/v1/config", views.config, name="headless_config"),
]
