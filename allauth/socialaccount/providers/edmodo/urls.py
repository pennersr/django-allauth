from allauth.socialaccount.providers.edmodo.provider import EdmodoProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EdmodoProvider)
