from django.conf.urls import patterns, url

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FacebookProvider
from . import views

urlpatterns = default_urlpatterns(FacebookProvider)

urlpatterns += patterns('',
   url('^facebook/login/token/$', views.login_by_token, 
       name="facebook_login_by_token"),
   url('^facebook/channel/$', views.channel, name='facebook_channel'),
   )
