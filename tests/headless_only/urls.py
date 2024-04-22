from django.urls import include, path


urlpatterns = [
    path("_allauth/", include("allauth.headless.urls")),
]
