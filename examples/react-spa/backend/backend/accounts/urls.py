from django.contrib import admin
from django.urls import include, path

from backend.accounts import views


urlpatterns = [
    path("profile/", views.profile),
]
