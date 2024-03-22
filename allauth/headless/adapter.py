from allauth.headless import app_settings
from allauth.utils import import_attribute


class DefaultHeadlessAdapter:
    """The adapter class allows you to override various functionality of the
    ``allauth.headless`` app.  To do so, point ``settings.HEADLESS_ADAPTER`` to your own
    class that derives from ``DefaultHeadlessAdapter`` and override the behavior by
    altering the implementation of the methods according to your own need.
    """

    pass


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
