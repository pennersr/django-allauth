from allauth.socialaccount.providers.jupyterhub_provider.provider import (
    JupyterHubProvider,
)
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(JupyterHubProvider)
