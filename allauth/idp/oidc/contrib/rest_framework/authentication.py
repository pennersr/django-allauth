from rest_framework.authentication import BaseAuthentication

from allauth.idp.oidc.internal.oauthlib.server import get_server
from allauth.idp.oidc.internal.oauthlib.utils import extract_params


class TokenAuthentication(BaseAuthentication):
    """
    Use the OIDC access token to authenticate the request.
    """

    def authenticate(self, request):
        server = get_server()
        orequest = extract_params(request)
        valid, ctx = server.verify_request(*orequest, scopes=[])
        if not valid:
            return None
        return ctx.user, ctx.access_token
