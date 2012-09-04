def account(request):
    # We used to have this due to the now removed
    # settings.CONTACT_EMAIL. Let's see if we need a context processor
    # in the future, otherwise, deprecate this context processor
    # completely.
    return { }
