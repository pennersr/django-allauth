from django.urls import include, path


urlpatterns = [
    path("idp/", include("tests.common.idp.urls")),
]
