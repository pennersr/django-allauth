from allauth.account.internal import flows
from allauth.usersessions.adapter import get_adapter
from allauth.usersessions.models import UserSession


def end_other_sessions(request, user):
    sessions_to_end = []
    for session in UserSession.objects.filter(user=user):
        if session.is_current():
            continue
        sessions_to_end.append(session)
    end_sessions(request, sessions_to_end)


def end_sessions(request, sessions):
    has_current = any([session.is_current() for session in sessions])
    get_adapter().end_sessions(sessions)
    if has_current:
        flows.logout.logout(request)
