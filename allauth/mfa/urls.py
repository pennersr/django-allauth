from django.urls import path

from allauth.mfa import views


urlpatterns = [
    path("authenticate/", views.authenticate, name="mfa_authenticate"),
]
