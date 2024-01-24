import requests
from urllib.parse import parse_qsl

from django.utils.translation import gettext as _

from requests_oauthlib import OAuth1

from allauth.socialaccount.providers.oauth.client import (
    OAuthClient,
    OAuthError,
    get_token_prefix,
)
from allauth.utils import get_request_param


class GarminConnectOAuthClient(OAuthClient):

    def get_access_token(self):
        """
        Garmin Connect expects oauth_verifier to be in the request header
        :return:
        """

        if self.access_token is None:
            request_token = self._get_rt_from_session()

            # Access token url
            at_url = self.access_token_url
            oauth_verifier = get_request_param(self.request, "oauth_verifier")

            oauth = OAuth1(
                self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=request_token["oauth_token"],
                resource_owner_secret=request_token["oauth_token_secret"],
                verifier=oauth_verifier,
            )

            # Get access token
            response = requests.post(url=at_url, auth=oauth)
            if response.status_code not in (200, 201):
                raise OAuthError(
                    _(
                        "Invalid response while obtaining access token"
                        ' from "%s". Response was: %s.'
                    )
                    % (get_token_prefix(self.access_token_url), response.text)
                )
            self.access_token = dict(parse_qsl(response.text))
            self.request.session[
                "oauth_%s_access_token" % get_token_prefix(self.access_token_url)
            ] = self.access_token

        return self.access_token
