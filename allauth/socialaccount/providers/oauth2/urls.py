from django.urls import include, path

from allauth.utils import import_attribute


def default_urlpatterns(provider):
    login_view = import_attribute(
        provider.get_package() + '.views.oauth2_login')
    callback_view = import_attribute(
        provider.get_package() + '.views.oauth2_callback')

    urlpatterns = [
        path('login/', login_view, name=provider.id + "_login"),
        path('login/callback/', callback_view, name=provider.id + "_callback"),
    ]

    return [path(provider.get_slug() + '/', include(urlpatterns))]
