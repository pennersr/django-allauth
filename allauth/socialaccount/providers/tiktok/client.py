from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class TikTokOAuth2Client(OAuth2Client):
    client_id_parameter = "client_key"
