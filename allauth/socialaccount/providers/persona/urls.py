from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url('^persona/login/$',
                           views.persona_login,
                           name="persona_login"))
