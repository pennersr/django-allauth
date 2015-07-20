from django.conf.urls import patterns, url
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import GoogleProvider
from .views import oauth2_callback_android

urlpatterns = default_urlpatterns(GoogleProvider)
urlpatterns += patterns('', url('^' + GoogleProvider.id + '/login/callback_android/$', oauth2_callback_android,
                               name=GoogleProvider.id + '_callback_android'))
