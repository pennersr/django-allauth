from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.conf.urls import patterns, url
from .provider import GoogleProvider
from . import views

urlpatterns = default_urlpatterns(GoogleProvider)

urlpatterns += patterns('',
   url('^google/login/token/$', views.login_by_token,
       name="google_login_by_token"),
   )
