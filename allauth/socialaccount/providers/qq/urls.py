from django.conf.urls import include, url

from allauth.utils import import_attribute
from .provider import QQProvider


def qq_urlpatterns(provider):
    login_view = import_attribute(
        provider.get_package() + '.views.oauth2_login')
    callback_view = import_attribute(
        provider.get_package() + '.views.oauth2_callback')

    urlpatterns = [
        url(r'^login/$',
            login_view, name=provider.id + "_login"),
        # remove the slash because of the QQ's strict rules of callback_url
        url(r'^login/callback$',
            callback_view, name=provider.id + "_callback"),
    ]

    return [url('^' + provider.get_slug() + '/', include(urlpatterns))]


urlpatterns = qq_urlpatterns(QQProvider)
