from django.conf import settings

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


provider_settings: dict = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get(
    "mediawiki", {}
)


class MediaWikiOAuth2Adapter(OAuth2Adapter):
    provider_id = "mediawiki"
    REST_API = provider_settings.get(
        "REST_API", "https://meta.wikimedia.org/w/rest.php"
    )
    access_token_url = REST_API + "/oauth2/access_token"
    authorize_url = REST_API + "/oauth2/authorize"
    profile_url = REST_API + "/oauth2/resource/profile"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "Bearer {token}".format(token=token.token)},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MediaWikiOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MediaWikiOAuth2Adapter)
