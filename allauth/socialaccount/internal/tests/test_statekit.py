from allauth.socialaccount.internal import statekit


def test_get_oldest_state():
    states = {
        "new": [{"id": "new"}, 300],
        "mid": [{"id": "mid"}, 200],
        "old": [{"id": "old"}, 100],
    }
    state_id, state = statekit.get_oldest_state(states)
    assert state_id == "old"
    assert state["id"] == "old"


def test_get_oldest_state_empty():
    state_id, state = statekit.get_oldest_state({})
    assert state_id is None
    assert state is None


def test_gc_states():
    states = {}
    for i in range(statekit.MAX_STATES + 1):
        states[f"state-{i}"] = [{"i": i}, 1000 + i]
    assert len(states) == statekit.MAX_STATES + 1
    statekit.gc_states(states)
    assert len(states) == statekit.MAX_STATES
    assert "state-0" not in states


def test_stashing(rf):
    request = rf.get("/")
    request.session = {}
    state_id = statekit.stash_state(request, {"foo": "bar"})
    state2_id = statekit.stash_state(request, {"foo2": "bar2"})
    state3_id = statekit.stash_state(request, {"foo3": "bar3"})
    state = statekit.unstash_last_state(request)
    assert state == {"foo3": "bar3"}
    state = statekit.unstash_state(request, state3_id)
    assert state is None
    state = statekit.unstash_state(request, state2_id)
    assert state == {"foo2": "bar2"}
    state = statekit.unstash_state(request, state2_id)
    assert state is None
    state = statekit.unstash_state(request, state_id)
    assert state == {"foo": "bar"}
    state = statekit.unstash_state(request, state_id)
    assert state is None
