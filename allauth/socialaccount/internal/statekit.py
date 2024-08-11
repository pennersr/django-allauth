import time
from typing import Any, Dict, Optional, Tuple

from allauth.socialaccount.adapter import get_adapter


STATE_ID_LENGTH = 16
MAX_STATES = 10
STATES_SESSION_KEY = "socialaccount_states"


def get_oldest_state(
    states: Dict[str, Tuple[Dict[str, Any], float]], rev: bool = False
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    oldest_ts = None
    oldest_id = None
    oldest = None
    for state_id, state_ts in states.items():
        ts = state_ts[1]
        if oldest_ts is None or (
            (rev and ts > oldest_ts) or ((not rev) and oldest_ts > ts)
        ):
            oldest_ts = ts
            oldest_id = state_id
            oldest = state_ts[0]
    return oldest_id, oldest


def gc_states(states: Dict[str, Tuple[Dict[str, Any], float]]):
    if len(states) > MAX_STATES:
        oldest_id, oldest = get_oldest_state(states)
        if oldest_id:
            del states[oldest_id]


def get_states(request) -> Dict[str, Tuple[Dict[str, Any], float]]:
    states = request.session.get(STATES_SESSION_KEY)
    if not isinstance(states, dict):
        states = {}
    return states


def stash_state(request, state: Dict[str, Any], state_id: Optional[str] = None) -> str:
    states = get_states(request)
    gc_states(states)
    if state_id is None:
        state_id = get_adapter().generate_state_param(state)
    states[state_id] = (state, time.time())
    request.session[STATES_SESSION_KEY] = states
    return state_id


def unstash_state(request, state_id: str) -> Optional[Dict[str, Any]]:
    state: Optional[Dict[str, Any]] = None
    states = get_states(request)
    state_ts = states.get(state_id)
    if state_ts is not None:
        state = state_ts[0]
        del states[state_id]
        request.session[STATES_SESSION_KEY] = states
    return state


def unstash_last_state(request) -> Optional[Dict[str, Any]]:
    states = get_states(request)
    state_id, state = get_oldest_state(states, rev=True)
    if state_id:
        unstash_state(request, state_id)
    return state
