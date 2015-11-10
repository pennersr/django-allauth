from django.conf.urls import url, include
from allauth.utils import import_attribute


def default_urlpatterns(provider):

    login_view = import_attribute(provider.package + '.views.oauth_login')
    callback_view = import_attribute(provider.package + '.views.oauth_callback')

    urlpatterns = [
        url('^login/$', login_view, name=provider.id + "_login"),
        url('^login/callback/$', callback_view, name=provider.id + "_callback"),
    ]

    return [url('^' + provider.id + '/', include(urlpatterns))]
