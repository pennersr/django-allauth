from allauth.headless.constants import Flow


def test_email_verification_rate_limits(
    client,
    db,
    user_password,
    settings,
    user_factory,
    password_factory,
    enable_cache,
    headless_reverse,
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_RATE_LIMITS = {"confirm_email": "1/m/key"}
    email = "user@email.org"
    user_factory(email=email, email_verified=False, password=user_password)
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": email,
                "password": user_password,
            },
            content_type="application/json",
        )
        if attempt == 0:
            assert resp.status_code == 401
            flow = [
                flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")
            ][0]
            assert flow["id"] == Flow.VERIFY_EMAIL
        else:
            assert resp.status_code == 400
            assert resp.json() == {
                "status": 400,
                "errors": [
                    {
                        "message": "Too many failed login attempts. Try again later.",
                        "code": "too_many_login_attempts",
                    }
                ],
            }
