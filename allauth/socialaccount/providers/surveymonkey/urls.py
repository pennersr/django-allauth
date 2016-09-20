from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import SurveyMonkey2Provider

urlpatterns = default_urlpatterns(SurveyMonkey2Provider)
