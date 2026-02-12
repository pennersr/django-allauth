from typing import Optional, Set

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def get_roles(request: HttpRequest) -> Set[str]:
    roles = request.session.get("kc_roles") or []
    return set(roles)


def role_for_app(roles: Set[str], app: str) -> Optional[str]:
    candidates = {r for r in roles if r.startswith(f"{app}:")}
    if f"{app}:read-write" in candidates:
        return f"{app}:read-write"
    if f"{app}:read" in candidates:
        return f"{app}:read"
    if f"{app}:none" in candidates:
        return f"{app}:none"
    return None


def require_app_access(request: HttpRequest, app: str) -> None:
    roles = get_roles(request)
    r = role_for_app(roles, app)

    # default deny if missing
    if r is None or r == f"{app}:none":
        raise PermissionDenied(f"No access to {app}")

    if request.method in SAFE_METHODS:
        # read is enough
        if r in (f"{app}:read", f"{app}:read-write"):
            return
        raise PermissionDenied(f"Read not allowed for {app}")

    # write methods
    if r == f"{app}:read-write":
        return
    raise PermissionDenied(f"Write not allowed for {app}")
