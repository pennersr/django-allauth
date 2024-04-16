from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class TiktokOAuth2Client(OAuth2Client):
    CLIENT_ID_PARAMETER = "client_key"
