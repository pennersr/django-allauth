from django.urls import path

from .views import ResourceView


urlpatterns = [
    path("resource", ResourceView.as_view(), name="idp_rest_framework_resource"),
]
