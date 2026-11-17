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


Expired Sessions
----------------

Expired Django sessions do not automatically remove their corresponding user
session records. Run the following command periodically to remove them::

    python manage.py clear_usersessions

``clear_usersessions`` uses a bulk database query with the ``db`` and
``cached_db`` session backends. With other backends it checks and deletes user
sessions in batches. To avoid checking every user session, records younger than
``SESSION_COOKIE_AGE`` are skipped and cleaned during a later run if they have
expired. The batch size can be adjusted using ``--batch-size``.
