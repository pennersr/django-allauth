from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
import requests
from .provider import SurveyMonkey2Provider



class SurveyMonkey2Adapter(OAuth2Adapter):
    provider_id = SurveyMonkey2Provider.id
    access_token_url = "https://api.surveymonkey.net/oauth/token"
    authorize_url = "https://api.surveymonkey.net/oauth/authorize"
    profile_url = "https://api.surveymonkey.net/v2/user/get_user_details"
    redirect_uri_protocol = 'http'

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": "bearer %s" % token,
            "Content-Type": "application/json"
        }

        extra_data = requests.post(self.profile_url, params={
            'api_key': app.key
        }, headers=headers)

        extra_data = extra_data.json()
        extra_data = extra_data['data']

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data
        )


oauth_login = OAuth2LoginView.adapter_view(SurveyMonkey2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(SurveyMonkey2Adapter)
