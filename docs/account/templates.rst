Template Tags
=============

Use ``user_display`` to render a user name without making assumptions on
how the user is represented (e.g. render the username, or first
name?)::

    {% load account %}

    {% user_display user %}

Or, if you need to use in a ``{% blocktrans %}``::

    {% load account %}

    {% user_display user as user_display %}
    {% blocktrans %}{{ user_display }} has logged in...{% endblocktrans %}

Then, override the ``ACCOUNT_USER_DISPLAY`` setting with your project
specific user display callable.

If you set ``ACCOUNT_USERNAME_REQUIRED = False`` and ``ACCOUNT_USER_MODEL_USERNAME_FIELD = None``,
then you can simply display the user.email with {{ user }}::

    In case you forgot, your username is {{ user }}.
