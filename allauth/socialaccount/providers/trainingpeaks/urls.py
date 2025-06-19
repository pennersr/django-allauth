from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.trainingpeaks.provider import TrainingPeaksProvider


urlpatterns = default_urlpatterns(TrainingPeaksProvider)
