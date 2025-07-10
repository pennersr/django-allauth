from django.conf import settings
from django.urls import resolve


def script_aware_resolve(path: str):
    """
    Django's reverse/resolve is asymmetric. reverse() adds `FORCE_SCRIPT_NAME`,
    yet, resolve() won't handle it.
    """
    if settings.FORCE_SCRIPT_NAME and path.startswith(settings.FORCE_SCRIPT_NAME):
        path = path.removeprefix(settings.FORCE_SCRIPT_NAME)
    return resolve(path)
