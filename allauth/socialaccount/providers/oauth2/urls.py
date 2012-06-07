from django.conf.urls.defaults import patterns, url, include


def default_urlpatterns(provider):
    urlpatterns = patterns(provider.package + '.views',
                           url('^login/$', 'oauth2_login', 
                               name=provider.id + "_login"),
                           url('^login/done/$', 'oauth2_complete',
                               name=provider.id + "_complete"))

    return patterns('', url('^' + provider.id + '/', include(urlpatterns)))
