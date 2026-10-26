from allauth.account.authentication import get_authentication_records
from allauth.account.internal.flows.login import record_authentication


def test_get_authentication_records_without_user_returns_no_records(
    request_factory, user, user_factory
):
    other_user = user_factory()
    request = request_factory.get("/")
    record_authentication(request, user, method="password")

    assert get_authentication_records(request) == []
    records = get_authentication_records(request, user)
    assert len(records) == 1
    assert records[0]["method"] == "password"

    record_authentication(request, other_user, method="code")

    assert get_authentication_records(request, user) == []
    records = get_authentication_records(request, other_user)
    assert len(records) == 1
    assert records[0]["method"] == "code"
