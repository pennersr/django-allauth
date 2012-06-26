from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from models import GoogleProvider

urlpatterns = default_urlpatterns(GoogleProvider)
