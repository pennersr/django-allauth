from allauth.headless.base.response import APIResponse
from allauth.usersessions import app_settings


class SessionsResponse(APIResponse):
    def __init__(self, request, sessions):
        super().__init__(request, data=[self._session_data(s) for s in sessions])

    def _session_data(self, session):
        data = {
            "user_agent": session.user_agent,
            "ip": session.ip,
            "created_at": session.created_at.timestamp(),
            "is_current": session.is_current(),
            "id": session.pk,
        }
        if app_settings.TRACK_ACTIVITY:
            data["last_seen_at"] = session.last_seen_at.timestamp()
        return data


def get_config_data(request):
    data = {"usersessions": {"track_activity": app_settings.TRACK_ACTIVITY}}
    return data
