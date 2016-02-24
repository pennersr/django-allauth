from django.conf.urls import url

from . import views

urlpatterns = [
    url('^persona/login/$', views.persona_login, name="persona_login")
]
