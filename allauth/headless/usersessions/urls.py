from django.urls import include, path

from allauth.headless.usersessions import views


urlpatterns = [
    path(
        "auth/",
        include(
            [
                path(
                    "sessions",
                    views.sessions,
                    name="headless_usersessions",
                ),
            ]
        ),
    )
]
