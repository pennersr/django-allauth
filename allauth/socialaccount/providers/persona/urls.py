from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
   url('^persona/login/$', views.persona_login, 
       name="persona_login"))
