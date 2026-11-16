from typing import Any

from django.http import HttpRequest

from allauth import app_settings as allauth_settings
from allauth.socialaccount.models import SocialAccount


BACKCHANNEL_LOGOUT_SESSION_KEY = "socialaccount_openid_connect_sessions"


def track_session(
    request: HttpRequest, provider_id: str, id_token: dict[str, Any]
) -> None:
    if not allauth_settings.USERSESSIONS_ENABLED:
        return
    if (sid := id_token.get("sid")) and (sub := id_token.get("sub")):
        sessions = dict(request.session.get(BACKCHANNEL_LOGOUT_SESSION_KEY, {}))
        sessions[provider_id] = {"sid": sid, "sub": sub}
        request.session[BACKCHANNEL_LOGOUT_SESSION_KEY] = sessions


def end_sessions(
    request: HttpRequest, *, provider_id: str, logout_data: dict[str, Any]
) -> bool:
    if not allauth_settings.USERSESSIONS_ENABLED:
        return False

    from allauth.usersessions.internal.flows.sessions import (
        end_sessions as end_user_sessions,
    )
    from allauth.usersessions.models import UserSession

    account = SocialAccount.objects.filter(
        provider=provider_id, uid=logout_data["sub"]
    ).first()
    if not account:
        return False

    sessions = UserSession.objects.filter(user_id=account.user_id)
    if sid := logout_data.get("sid"):
        matching_sessions = []
        for user_session in sessions.iterator():
            store = user_session._session_store(user_session.session_key)
            oidc_session = store.get(BACKCHANNEL_LOGOUT_SESSION_KEY, {}).get(
                provider_id, {}
            )
            if oidc_session.get("sid") == sid:
                matching_sessions.append(user_session)
        end_user_sessions(request, matching_sessions)
    else:
        end_user_sessions(request, sessions)

    return True
