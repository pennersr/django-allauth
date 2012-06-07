from django.conf.urls.defaults import patterns, url, include


def default_urlpatterns(provider):

    urlpatterns = patterns(provider.package + '.views',
                           url('^login/$', 'oauth_login',
                               name=provider.id + "_login"),
                           url('^callback/$', 'oauth_callback',
                               name=provider.id + "_callback"),
                           url('^login/done/$', 'oauth_complete',
                               name=provider.id + "_complete"))

    return patterns('', url('^' + provider.id + '/', include(urlpatterns)))
