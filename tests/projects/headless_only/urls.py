from django.urls import include, path


urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("", include("tests.projects.common.urls")),
]
