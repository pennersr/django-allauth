from django.urls import include, path


urlpatterns = [
    path("drf/", include("tests.common.idp.rest_framework.urls")),
    path("ninja/", include("tests.common.idp.ninja.urls")),
]
