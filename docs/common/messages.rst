Messages
========

The Django messages framework (``django.contrib.messages``) is used if
it is listed in ``settings.INSTALLED_APPS``.  All messages (as in
``django.contrib.messages``) are configurable by overriding their
respective template. If you want to disable a message, simply override
the message template with a blank one.
