# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Auth0Account(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(Auth0Account, self).to_str()
        return self.account.extra_data.get('name', dflt)


class Auth0Provider(OAuth2Provider):
    id = 'auth0'
    name = 'Auth0'
    account_class = Auth0Account

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=data.get('name'),
            user_id=data.get('user_id'),
            picture=data.get('picture'),
        )


provider_classes = [Auth0Provider]
