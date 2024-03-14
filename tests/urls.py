from django.urls import include, path


urlpatterns = [
    path("", include("allauth.urls")),
]
