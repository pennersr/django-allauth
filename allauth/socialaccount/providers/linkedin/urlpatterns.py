from allauth.socialaccount.providers.oauth.urlpatterns import default_urlpatterns
from models import LinkedInProvider

urlpatterns = default_urlpatterns(LinkedInProvider)

