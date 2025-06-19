from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.jupyterhub.views import JupyterHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class JupyterHubAccount(ProviderAccount):
    pass


class JupyterHubProvider(OAuth2Provider):
    id = "jupyterhub"
    name = "JupyterHub"
    account_class = JupyterHubAccount
    oauth2_adapter_class = JupyterHubOAuth2Adapter

    def extract_uid(self, data):
        return str(data.get("name"))

    def extract_common_fields(self, data):
        return dict(name=data.get("name", ""))


provider_classes = [JupyterHubProvider]
