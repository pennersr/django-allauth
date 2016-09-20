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
        raise wtf
        return data['userdetails']["user_id"]

    def extract_common_fields(self, data):
        raise wtf
        return dict(name=data["userdetails"].get('username'))
                    # email=data.get('email'))

providers.registry.register(SurveyMonkey2Provider)
