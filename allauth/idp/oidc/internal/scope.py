from allauth.idp.oidc.models import Token


def _is_scope_granted(
    scope: str | list[str] | list[list[str]],
    granted_scope: list[str],
) -> bool:
    if isinstance(scope, str):
        return scope in granted_scope
    if not isinstance(scope, list):
        raise ValueError
    if len(scope) == 0:
        return True
    list_of_list_of_scopes: list[list[str]]
    if isinstance(scope[0], str):
        list_of_list_of_scopes = [scope]  # type: ignore
    else:
        list_of_list_of_scopes = scope  # type: ignore
    for list_of_scopes in list_of_list_of_scopes:
        if all(s in granted_scope for s in list_of_scopes):
            return True
    return False


def is_scope_granted(
    scope: (
        None
        | str
        | list[str]
        | list[list[str]]
        | dict[str, str | list[str] | list[list[str]]]
    ),
    token: Token,
    method: str | None = None,
) -> bool:
    if scope is None:
        return True
    if isinstance(scope, dict):
        if not method:
            return False
        scope = scope.get(method)
    granted_scope = token.get_scopes() if token else []
    assert scope is not None  # nosec
    return _is_scope_granted(scope, granted_scope)
