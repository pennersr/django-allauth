from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SurveyMonkeyOAuth2Account(ProviderAccount):
    pass


class SurveyMonkey2Provider(OAuth2Provider):
    id = 'surveymonkey'
    name = 'SurveyMonkey'
    account_class = SurveyMonkeyOAuth2Account

    def extract_uid(self, data):
        return data['user_details']["user_id"]

    def extract_common_fields(self, data):
        return dict(data["user_details"])

providers.registry.register(SurveyMonkey2Provider)
