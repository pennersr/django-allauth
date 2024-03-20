from django.urls import path

from allauth.headless.base import views


urlpatterns = [
    path("config", views.config, name="headless_config"),
]
