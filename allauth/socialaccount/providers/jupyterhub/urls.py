from allauth.socialaccount.providers.jupyterhub.provider import (
    JupyterHubProvider,
)
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(JupyterHubProvider)
