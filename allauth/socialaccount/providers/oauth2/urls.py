from django.urls import include, path

from allauth.utils import import_attribute


def default_urlpatterns(provider):
    login_view = import_attribute(f"{provider.get_package()}.views.oauth2_login")
    callback_view = import_attribute(f"{provider.get_package()}.views.oauth2_callback")

    urlpatterns = [
        path("login/", login_view, name=f"{provider.id}_login"),
        path("login/callback/", callback_view, name=f"{provider.id}_callback"),
    ]

    return [path(f"{provider.get_slug()}/", include(urlpatterns))]
