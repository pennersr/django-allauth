from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import MRUProvider

urlpatterns = default_urlpatterns(MRUProvider)
