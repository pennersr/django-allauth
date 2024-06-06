from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import TrainingPeaksProvider


urlpatterns = default_urlpatterns(TrainingPeaksProvider)
