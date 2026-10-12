from __future__ import annotations

import time
from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from allauth.socialaccount.adapter import get_adapter


STATE_ID_LENGTH = 16
MAX_STATES = 10
STATE_TTL = 600
STATES_SESSION_KEY = "socialaccount_states"

StashedState = tuple[dict[str, Any], float, str]


def get_oldest_state(
    states: dict[str, StashedState],
    *,
    rev: bool = False,
    provider_id: str | None = None,
) -> str | None:
    oldest_ts = None
    oldest_id = None
    for state_id, stashed_state in states.items():
        if provider_id is not None and (
            len(stashed_state) != 3 or stashed_state[2] != provider_id
        ):
            continue
        ts = stashed_state[1]
        if oldest_ts is None or (
            (rev and ts > oldest_ts) or ((not rev) and oldest_ts > ts)
        ):
            oldest_ts = ts
            oldest_id = state_id
    return oldest_id


def gc_states(states: dict[str, StashedState]) -> None:
    now = time.time()
    expired_sids = [
        sid
        for sid, stashed_state in states.items()
        if now - stashed_state[1] > STATE_TTL
    ]
    for sid in expired_sids:
        del states[sid]
    if len(states) > MAX_STATES:
        oldest_id = get_oldest_state(states)
        if oldest_id:
            del states[oldest_id]


def get_states(request: HttpRequest) -> dict[str, StashedState]:
    states = request.session.get(STATES_SESSION_KEY)
    if not isinstance(states, dict):
        states = {}
    return states


def stash_state(
    request: HttpRequest,
    *,
    provider_id: str,
    state: dict[str, Any],
    state_id: str | None = None,
) -> str:
    states = get_states(request)
    gc_states(states)
    if state_id is None:
        state_id = get_adapter().generate_state_param(state)
    states[state_id] = (state, time.time(), provider_id)
    request.session[STATES_SESSION_KEY] = states
    return state_id


def unstash_state(
    request: HttpRequest, *, state_id: str, provider_id: str, raises: bool = False
) -> dict[str, Any] | None:
    state: dict[str, Any] | None = None
    states = get_states(request)
    stashed_state = states.get(state_id)
    if (
        stashed_state is not None
        and len(stashed_state) == 3
        and stashed_state[2] == provider_id
    ):
        state, ts, _ = stashed_state
        if time.time() - ts > STATE_TTL:
            state = None
        del states[state_id]
        request.session[STATES_SESSION_KEY] = states
    if state is None and raises:
        raise PermissionDenied()
    return state


def unstash_last_state(
    request: HttpRequest, *, provider_id: str, raises: bool = False
) -> dict[str, Any] | None:
    states = get_states(request)
    state_id = get_oldest_state(states, rev=True, provider_id=provider_id)
    if state_id:
        return unstash_state(
            request,
            state_id=state_id,
            provider_id=provider_id,
            raises=raises,
        )
    if raises:
        raise PermissionDenied()
    return None
