from django.urls import path

from allauth.headless.usersessions import views


urlpatterns = [
    path(
        "v1/sessions",
        views.sessions,
        name="headless_usersessions",
    ),
]
