from django.conf.urls.defaults import *
import app_settings

urlpatterns = patterns('',
                       url('^', include('allauth.account.urls')),
                       url('^social/', include('allauth.socialaccount.urls')))

if app_settings.TWITTER_ENABLED:
    urlpatterns += patterns('',
                            url('^twitter/', include('allauth.twitter.urls')))
if app_settings.FACEBOOK_ENABLED:
    urlpatterns += patterns('',
                            url('^facebook/', include('allauth.facebook.urls')))
if app_settings.OPENID_ENABLED:
    urlpatterns += patterns('',
                            url('^openid/', include('allauth.openid.urls')))
