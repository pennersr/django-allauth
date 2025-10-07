from typing import Optional

from django.http import HttpRequest

from allauth.account.internal.flows.logout import logout
from allauth.idp.oidc.models import Client, Token


def rp_initiated_logout(
    request: HttpRequest,
    *,
    from_op: bool,
    post_logout_redirect_uri: Optional[str] = None,
    client: Optional[Client] = None,
):
    if not request.user.is_authenticated:
        return
    if client:
        Token.objects.filter(
            user=request.user,
            client=client,
            type__in=[Token.Type.ACCESS_TOKEN, Token.Type.REFRESH_TOKEN],
        ).delete()
    if from_op:
        has_redirect_uri = bool(post_logout_redirect_uri)
        logout(request, show_message=not has_redirect_uri)
