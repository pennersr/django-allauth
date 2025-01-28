from django.urls import path

from backend.ninja_demo import views


urlpatterns = [
    path("api/", views.api.urls),
]
