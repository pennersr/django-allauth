from django.urls import include, path


urlpatterns = [
    path("", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
]
