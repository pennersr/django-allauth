from django.urls import path

from allauth.headless.spec import views


urlpatterns = [
    path("openapi.yaml", views.OpenAPIYAMLView.as_view(), name="openapi_yaml"),
    path("openapi.json", views.OpenAPIJSONView.as_view(), name="openapi_json"),
    path("docs", views.OpenAPIDocumentationView.as_view(), name="openapi_doc"),
]
