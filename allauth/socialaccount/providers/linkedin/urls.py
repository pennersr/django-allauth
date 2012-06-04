from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from models import LinkedInProvider

urlpatterns = default_urlpatterns(LinkedInProvider)

