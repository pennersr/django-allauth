from django.urls import path

from . import views


urlpatterns = [path("persona/login/", views.persona_login, name="persona_login")]
