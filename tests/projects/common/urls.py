from django.urls import include, path


urlpatterns = [
    path("idp/", include("tests.projects.common.idp.urls")),
]
