import jwt
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.openid_connect.views import OpenIDConnectAdapter

from .provider import CernProvider


class CernOIDCAdapter(OpenIDConnectAdapter):
    provider_id = CernProvider.id
    supports_state = False

    def complete_login(self, request, app, token, response):
        # All required data can be found within either the access_token
        # or the id_token. To decode, we will also need the publick key from
        # the jwks url.

        key = jwt.PyJWKClient(self.openid_config["jwks_uri"]).get_signing_keys()[0]

        extra_data = jwt.decode(
            jwt=response["id_token"],
            key=key.key,
            algorithms=["RS256"],
            audience=app.client_id,
        )

        # Groups are no longer provided, and they have been replaced
        # by cern_roles.

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(CernOIDCAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CernOIDCAdapter)
