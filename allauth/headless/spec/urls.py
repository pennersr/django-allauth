from django.urls import path

from allauth.headless import app_settings
from allauth.headless.spec import views


urlpatterns = [
    path("openapi.yaml", views.OpenAPIYAMLView.as_view(), name="openapi_yaml"),
    path("openapi.json", views.OpenAPIJSONView.as_view(), name="openapi_json"),
]

if app_settings.SERVE_SPECIFICATION and app_settings.SPECIFICATION_TEMPLATE_NAME:
    urlpatterns.append(
        path(
            "openapi.html",
            views.OpenAPIHTMLView.as_view(),
            name="openapi_html",
        ),
    )
