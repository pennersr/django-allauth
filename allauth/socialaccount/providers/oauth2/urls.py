from django.conf.urls import patterns, url, include

from allauth.account import app_settings
from allauth.socialaccount.providers.oauth2.views import proxy_login_callback

def default_urlpatterns(provider):
    urlpatterns = patterns(provider.package + '.views',
                           url('^login/$', 'oauth2_login',
                               name=provider.id + "_login"),
                           url('^login/callback/$', 'oauth2_callback',
                               name=provider.id + '_callback'))

    if app_settings.LOGIN_PROXY_REDIRECT_WHITELIST:
        urlpatterns += patterns('',
            url('^login/callback/proxy/$',
                proxy_login_callback,
                {'callback_view_name': provider.id + '_callback'},
                name=provider.id + '_proxy')
        )
    return patterns('', url('^' + provider.id + '/', include(urlpatterns)))
