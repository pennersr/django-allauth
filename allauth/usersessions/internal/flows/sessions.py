from allauth.account.internal import flows
from allauth.usersessions.adapter import get_adapter


def end_sessions(request, sessions):
    has_current = any([session.is_current() for session in sessions])
    get_adapter().end_sessions(sessions)
    if has_current:
        flows.logout.logout(request)
