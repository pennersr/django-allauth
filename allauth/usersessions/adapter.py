from allauth.usersessions import app_settings
from allauth.utils import import_attribute


class DefaultUserSessionsAdapter:
    """The adapter class allows you to override various functionality of the
    ``allauth.usersessions`` app.  To do so, point ``settings.USERSESSIONS_ADAPTER`` to your own
    class that derives from ``DefaultUserSessionsAdapter`` and override the behavior by
    altering the implementation of the methods according to your own need.
    """

    def end_sessions(self, sessions):
        for session in sessions:
            session.end()


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
