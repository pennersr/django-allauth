from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from provider import TwitterProvider
from django.conf.urls import patterns, url
from views import oauth_authorize

urlpatterns = default_urlpatterns(TwitterProvider)
urlpatterns += patterns('',
                        url('^' + TwitterProvider.id + '/authorize/$', oauth_authorize,
                            name=TwitterProvider.id + '_authorize'),
)
