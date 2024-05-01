import time

from allauth.socialaccount.adapter import get_adapter


STATE_ID_LENGTH = 16
MAX_STATES = 10
STATES_SESSION_KEY = "socialaccount_states"


def get_oldest_state(states, rev=False):
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


def gc_states(states):
    if len(states) > MAX_STATES:
        oldest_id, oldest = get_oldest_state(states)
        if oldest_id:
            del states[oldest_id]


def get_states(request):
    states = request.session.get(STATES_SESSION_KEY)
    if not isinstance(states, dict):
        states = {}
    return states


def stash_state(request, state):
    states = get_states(request)
    gc_states(states)
    state_id = get_adapter().generate_state_param(state)
    states[state_id] = (state, time.time())
    request.session[STATES_SESSION_KEY] = states
    return state_id


def unstash_state(request, state_id):
    state = None
    states = get_states(request)
    if state_id in states:
        state_ts = states.get(state_id)
        state = state_ts[0]
        del states[state_id]
        request.session[STATES_SESSION_KEY] = states
    return state


def unstash_last_state(request):
    states = get_states(request)
    state_id, state = get_oldest_state(states, rev=True)
    if state_id:
        unstash_state(request, state_id)
    return state
