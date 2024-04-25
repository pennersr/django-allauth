from django.urls import path

from backend.accounts import views


urlpatterns = [
    path("profile/", views.profile),
]
