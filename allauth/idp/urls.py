from django.urls import include, path


app_name = "idp"
urlpatterns = [
    path("", include("allauth.idp.oidc.urls")),
]
