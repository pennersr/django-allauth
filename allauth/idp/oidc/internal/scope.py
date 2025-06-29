from typing import Dict, List, Optional, Union

from allauth.idp.oidc.models import Token


def _is_scope_granted(
    scope: Union[
        str,
        List[str],
        List[List[str]],
    ],
    granted_scope: List[str],
) -> bool:
    if isinstance(scope, str):
        return scope in granted_scope
    if not isinstance(scope, list):
        raise ValueError
    if len(scope) == 0:
        return True
    list_of_list_of_scopes: List[List[str]]
    if isinstance(scope[0], str):
        list_of_list_of_scopes = [scope]  # type: ignore
    else:
        list_of_list_of_scopes = scope  # type: ignore
    for list_of_scopes in list_of_list_of_scopes:
        if all(s in granted_scope for s in list_of_scopes):
            return True
    return False


def is_scope_granted(
    scope: Union[
        None,
        str,
        List[str],
        List[List[str]],
        Dict[str, Union[str, List[str], List[List[str]]]],
    ],
    token: Token,
    method: Optional[str] = None,
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
