from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class MediaWikiOAuth2Adapter(OAuth2Adapter):
    provider_id = "mediawiki"
    settings = app_settings.PROVIDERS.get(provider_id, {})
    REST_API = settings.get("REST_API", "https://meta.wikimedia.org/w/rest.php")
    access_token_url = f"{REST_API}/oauth2/access_token"
    authorize_url = f"{REST_API}/oauth2/authorize"
    profile_url = f"{REST_API}/oauth2/resource/profile"
    # Allow custom User-Agent per Wikimedia policy.
    headers = {"User-Agent": settings.get("USER_AGENT", "django-allauth")}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}", **self.headers}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MediaWikiOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MediaWikiOAuth2Adapter)
