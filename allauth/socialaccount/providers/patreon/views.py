"""
Views for PatreonProvider
https://www.patreon.com/platform/documentation/oauth
"""

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import API_URL, USE_API_V2, PatreonProvider


class PatreonOAuth2Adapter(OAuth2Adapter):
    provider_id = PatreonProvider.id
    access_token_url = "https://www.patreon.com/api/oauth2/token"
    authorize_url = "https://www.patreon.com/oauth2/authorize"
    profile_url = "{0}/{1}".format(
        API_URL,
        "identity?include=memberships&fields%5Buser%5D=email,first_name,"
        "full_name,image_url,last_name,social_connections,"
        "thumb_url,url,vanity"
        if USE_API_V2
        else "current_user",
    )

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "Bearer " + token.token},
            )
        )
        extra_data = resp.json().get("data")

        if USE_API_V2:
            # Extract tier/pledge level for Patreon API v2:
            try:
                member_id = extra_data["relationships"]["memberships"]["data"][0]["id"]
                member_url = (
                    "{0}/members/{1}?include="
                    "currently_entitled_tiers&fields%5Btier%5D=title"
                ).format(API_URL, member_id)
                resp_member = (
                    get_adapter()
                    .get_requests_session()
                    .get(
                        member_url,
                        headers={"Authorization": "Bearer " + token.token},
                    )
                )
                pledge_title = resp_member.json()["included"][0]["attributes"]["title"]
                extra_data["pledge_level"] = pledge_title
            except (KeyError, IndexError):
                extra_data["pledge_level"] = None
                pass

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PatreonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PatreonOAuth2Adapter)
