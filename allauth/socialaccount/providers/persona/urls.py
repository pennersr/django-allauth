from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
   url('^persona/login/$', views.persona_login, 
       name="persona_login"))
