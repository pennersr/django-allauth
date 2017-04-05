from django.conf.urls import url

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from . import views
from .provider import FacebookProvider


urlpatterns = default_urlpatterns(FacebookProvider)

urlpatterns += [
    url(r'^facebook/login/token/$',
        views.login_by_token,
        name="facebook_login_by_token"),
]
