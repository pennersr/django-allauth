from __future__ import annotations

from django.http import HttpRequest
from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class FlickrAPI(OAuth):
    api_url = "https://api.flickr.com/services/rest"

    def get_user_info(self):
        default_params = {"nojsoncallback": "1", "format": "json"}
        p = dict({"method": "flickr.test.login"}, **default_params)
        u = self.query(f"{self.api_url}?{urlencode(p)}").json()

        p = dict(
            {"method": "flickr.people.getInfo", "user_id": u["user"]["id"]},
            **default_params,
        )
        user = self.query(f"{self.api_url}?{urlencode(p)}").json()
        return user


class FlickrOAuthAdapter(OAuthAdapter):
    provider_id = "flickr"
    request_token_url = "https://www.flickr.com/services/oauth/request_token"  # nosec
    access_token_url = "https://www.flickr.com/services/oauth/access_token"  # nosec
    authorize_url = "https://www.flickr.com/services/oauth/authorize"

    def complete_login(self, request: HttpRequest, app, token, **kwargs):
        client = FlickrAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(FlickrOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(FlickrOAuthAdapter)
