Installation
============

On top of the standard installation, add the following::

    INSTALLED_APPS = [
        ...
        'django.contrib.humanize',
        'allauth.usersessions',
        ...
    ]

    MIDDLEWARE = [
        ...
        # Optional -- needed when: USERSESSIONS_TRACK_ACTIVITY = True
        'allauth.usersessions.middleware.UserSessionsMiddleware',
        ...
    ]

Keep in mind that ``allauth.usersessions.middleware.UserSessionsMiddleware`` needs to be before ``django.contrib.auth.middleware.AuthenticationMiddleware``.
