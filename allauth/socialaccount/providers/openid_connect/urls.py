from django.conf.urls import patterns, url, include


def default_urlpatterns(provider):
    urlpatterns = patterns(provider.package + '.views',
                           url('^login/$', 'oauth2_login', 
                               name=provider.id + "_login"),
                           url('^login/callback/$', 'oauth2_callback',
                               name=provider.id + "_callback"))

    return patterns('', url('^' + provider.id + '/', include(urlpatterns)))
