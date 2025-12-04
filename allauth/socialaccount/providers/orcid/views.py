from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class OrcidOAuth2Adapter(OAuth2Adapter):
    provider_id = "orcid"
    member_api_default = False
    base_domain_default = "orcid.org"

    settings = app_settings.PROVIDERS.get(provider_id, {})

    base_domain = settings.get("BASE_DOMAIN", base_domain_default)
    member_api = settings.get("MEMBER_API", member_api_default)

    api_domain = f"{'api' if member_api else 'pub'}.{base_domain}"

    authorize_url = f"https://{base_domain}/oauth/authorize"
    access_token_url = f"https://{api_domain}/oauth/token"
    profile_url = f"https://{api_domain}/v3.0/%s/record"

    def complete_login(self, request, app, token, **kwargs):
        params = {}
        if self.member_api:
            params["access_token"] = token.token

        headers = {"accept": "application/orcid+json"}
        with get_adapter().get_requests_session() as sess:
            url = self.profile_url % kwargs["response"]["orcid"]
            resp = sess.get(url, params=params, headers=headers)
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OrcidOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OrcidOAuth2Adapter)
