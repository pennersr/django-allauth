from allauth.socialaccount.providers.disqus.provider import DisqusProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DisqusProvider)
