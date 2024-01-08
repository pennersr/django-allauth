from allauth.account.forms import ResetPasswordForm


def test_user_email_unicode_collision(settings, rf, user_factory, mailoutbox):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    user_factory(username="mike123", email="mike@example.org")
    user_factory(username="mike456", email="mıke@example.org")
    data = {"email": "mıke@example.org"}
    form = ResetPasswordForm(data)
    assert form.is_valid()
    form.save(rf.get("/"))
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["mıke@example.org"]


def test_user_email_domain_unicode_collision(settings, rf, user_factory, mailoutbox):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    user_factory(username="mike123", email="mike@ixample.org")
    user_factory(username="mike456", email="mike@ıxample.org")
    data = {"email": "mike@ıxample.org"}
    form = ResetPasswordForm(data)
    assert form.is_valid()
    form.save(rf.get("/"))
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["mike@ıxample.org"]


def test_user_email_unicode_collision_nonexistent(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    user_factory(username="mike123", email="mike@example.org")
    data = {"email": "mıke@example.org"}
    form = ResetPasswordForm(data)
    assert not form.is_valid()


def test_user_email_domain_unicode_collision_nonexistent(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    user_factory(username="mike123", email="mike@ixample.org")
    data = {"email": "mike@ıxample.org"}
    form = ResetPasswordForm(data)
    assert not form.is_valid()
