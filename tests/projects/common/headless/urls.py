from django.urls import include, path


urlpatterns = [
    path("drf/", include("tests.projects.common.headless.rest_framework.urls")),
    path("ninja/", include("tests.projects.common.headless.ninja.urls")),
]
