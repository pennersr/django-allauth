from http import HTTPStatus
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth.client import (
    OAuthClient,
    OAuthError,
    get_token_prefix,
)
from allauth.utils import build_absolute_uri


class PocketOAuthClient(OAuthClient):
    def _get_request_token(self):
        """
        Obtain a temporary request token to authorize an access token and to
        sign the request to obtain the access token
        """
        if self.request_token is None:
            redirect_url = build_absolute_uri(self.request, self.callback_url)
            headers = {
                "X-Accept": "application/json",
            }
            data = {
                "consumer_key": self.consumer_key,
                "redirect_uri": redirect_url,
            }
            response = (
                get_adapter()
                .get_requests_session()
                .post(
                    url=self.request_token_url,
                    json=data,
                    headers=headers,
                )
            )
            if response.status_code != HTTPStatus.OK:
                raise OAuthError(
                    _("Invalid response while obtaining request token" ' from "%s".')
                    % get_token_prefix(self.request_token_url)
                )
            self.request_token = response.json()["code"]
            self.request.session[
                "oauth_%s_request_token" % get_token_prefix(self.request_token_url)
            ] = self.request_token
        return self.request_token

    def get_redirect(self, authorization_url, extra_params):
        """
        Returns a ``HttpResponseRedirect`` object to redirect the user
        to the Pocket authorization URL.
        """
        request_token = self._get_request_token()
        params = {
            "request_token": request_token,
            "redirect_uri": self.request.build_absolute_uri(self.callback_url),
        }
        params.update(extra_params)
        url = authorization_url + "?" + urlencode(params)
        return HttpResponseRedirect(url)

    def get_access_token(self):
        """
        Obtain the access token to access private resources at the API
        endpoint.
        """
        if self.access_token is None:
            request_token = self._get_rt_from_session()
            url = self.access_token_url
            headers = {
                "X-Accept": "application/json",
            }
            data = {
                "consumer_key": self.consumer_key,
                "code": request_token,
            }
            response = (
                get_adapter()
                .get_requests_session()
                .post(url=url, headers=headers, json=data)
            )
            if response.status_code != HTTPStatus.OK:
                raise OAuthError(
                    _("Invalid response while obtaining access token" ' from "%s".')
                    % get_token_prefix(self.request_token_url)
                )
            r = response.json()
            self.access_token = {
                "oauth_token": request_token,
                "oauth_token_secret": r["access_token"],
                "username": r["username"],
            }

            self.request.session[
                "oauth_%s_access_token" % get_token_prefix(self.request_token_url)
            ] = self.access_token
        return self.access_token
