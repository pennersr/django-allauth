import time

from django.core.exceptions import PermissionDenied

import pytest

from allauth.socialaccount.internal import statekit


def test_get_oldest_state():
    states = {
        "new": [{"id": "new"}, 300, "provider"],
        "mid": [{"id": "mid"}, 200, "provider"],
        "old": [{"id": "old"}, 100, "provider"],
    }
    state_id = statekit.get_oldest_state(states)
    assert state_id == "old"


def test_get_oldest_state_empty():
    state_id = statekit.get_oldest_state({})
    assert state_id is None


def test_gc_states():
    now = time.time()
    states = {}
    for i in range(statekit.MAX_STATES + 1):
        states[f"state-{i}"] = [{"i": i}, now + i, "provider"]
    assert len(states) == statekit.MAX_STATES + 1
    statekit.gc_states(states)
    assert len(states) == statekit.MAX_STATES
    assert "state-0" not in states


def test_gc_states_expires():
    now = time.time()
    states = {
        "fresh": [{"id": "fresh"}, now, "provider"],
        "expired": [
            {"id": "expired"},
            now - statekit.STATE_TTL - 1,
            "provider",
        ],
    }
    statekit.gc_states(states)
    assert "fresh" in states
    assert "expired" not in states


def test_stashing(rf):
    request = rf.get("/")
    request.session = {}
    provider_id = "provider"

    # Stash states with a small delay
    state_id = statekit.stash_state(
        request, provider_id=provider_id, state={"foo": "bar"}
    )
    time.sleep(0.001)  # delay for microseconds
    state2_id = statekit.stash_state(
        request, provider_id=provider_id, state={"foo2": "bar2"}
    )
    time.sleep(0.001)  # delay for microseconds
    state3_id = statekit.stash_state(
        request, provider_id=provider_id, state={"foo3": "bar3"}
    )

    # Unstash last state and check order
    state = statekit.unstash_last_state(request, provider_id=provider_id)
    assert state == {"foo3": "bar3"}

    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state3_id)
    assert state is None
    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state2_id)
    assert state == {"foo2": "bar2"}
    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state2_id)
    assert state is None
    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state_id)
    assert state == {"foo": "bar"}
    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state_id)
    assert state is None


def test_unstash_expired_state(rf):
    request = rf.get("/")
    request.session = {}
    provider_id = "provider"
    state_id = statekit.stash_state(
        request, provider_id=provider_id, state={"foo": "bar"}
    )
    # Backdate the timestamp to simulate expiry
    states = statekit.get_states(request)
    states[state_id] = (
        states[state_id][0],
        time.time() - statekit.STATE_TTL - 1,
        provider_id,
    )
    request.session[statekit.STATES_SESSION_KEY] = states
    state = statekit.unstash_state(request, provider_id=provider_id, state_id=state_id)
    assert state is None


def test_unstash_state_raises(rf):
    request = rf.get("/")
    request.session = {}
    state_id = statekit.stash_state(
        request, provider_id="provider", state={"foo": "bar"}
    )

    with pytest.raises(PermissionDenied):
        statekit.unstash_state(
            request, provider_id="other-provider", state_id=state_id, raises=True
        )
