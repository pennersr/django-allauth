from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class DataportenOAuth2Adapter(OAuth2Adapter):
    provider_id = "dataporten"
    access_token_url = "https://auth.dataporten.no/oauth/token"
    authorize_url = "https://auth.dataporten.no/oauth/authorization"
    profile_url = "https://auth.dataporten.no/userinfo"
    groups_url = "https://groups-api.dataporten.no/groups/"

    def complete_login(self, request, app, token, **kwargs):
        """
        Arguments:
            request - The get request to the callback URL
                        /accounts/dataporten/login/callback.
            app - The corresponding SocialApp model instance
            token - A token object with access token given in token.token
        Returns:
            Should return a dict with user information intended for parsing
            by the methods of the DataportenProvider view, i.e.
            extract_uid(), extract_extra_data(), and extract_common_fields()
        """
        # The authentication header
        headers = {"Authorization": "Bearer " + token.token}

        # Userinfo endpoint, for documentation see:
        # https://docs.dataporten.no/docs/oauth-authentication/
        userinfo_response = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers=headers,
            )
        )
        # Raise exception for 4xx and 5xx response codes
        userinfo_response.raise_for_status()

        # The endpoint returns json-data and it needs to be decoded
        extra_data = userinfo_response.json()["user"]

        # Finally test that the audience property matches the client id
        # for validification reasons, as instructed by the Dataporten docs
        # if the userinfo-response is used for authentication
        if userinfo_response.json()["audience"] != app.client_id:
            raise ProviderException(
                "Dataporten returned a user with an audience field \
                 which does not correspond to the client id of the \
                 application."
            )

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data,
        )


oauth2_login = OAuth2LoginView.adapter_view(DataportenOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DataportenOAuth2Adapter)
