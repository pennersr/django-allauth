from django.urls import include, path


urlpatterns = [
    path("idp/", include("tests.projects.common.idp.urls")),
    path("account/", include("tests.projects.common.account.urls")),
]
