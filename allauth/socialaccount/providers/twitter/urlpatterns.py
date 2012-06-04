from allauth.socialaccount.providers.oauth.urlpatterns import default_urlpatterns
from models import TwitterProvider

urlpatterns = default_urlpatterns(TwitterProvider)

