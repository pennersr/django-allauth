Installation
============

Django
------

Python package::

    pip install django-allauth

settings.py::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        # Required by `allauth` template tags
        'django.core.context_processors.request',
        ...
        # `allauth` specific context processors
        'allauth.account.context_processors.account',
        'allauth.socialaccount.context_processors.socialaccount',
        ...
    )

If you are running Django 1.8+, you can specify the context like so:

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # Already defined Django-related contexts here

                    # All Auth needs this from django
                    'django.core.context_processors.request',
                    
                    # `allauth` specific context processors
                    'allauth.account.context_processors.account',
                    'allauth.socialaccount.context_processors.socialaccount',
                ],
            },
        },
    ]

    AUTHENTICATION_BACKENDS = (
        ...
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',

        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
        ...
    )

    INSTALLED_APPS = (
        ...
        # The Django sites framework is required
        'django.contrib.sites',

        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # ... include the providers you want to enable:
        'allauth.socialaccount.providers.amazon',
        'allauth.socialaccount.providers.angellist',
        'allauth.socialaccount.providers.bitbucket',
        'allauth.socialaccount.providers.bitly',
        'allauth.socialaccount.providers.coinbase',
        'allauth.socialaccount.providers.dropbox',
        'allauth.socialaccount.providers.dropbox_oauth2',
        'allauth.socialaccount.providers.evernote',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.flickr',
        'allauth.socialaccount.providers.feedly',
        'allauth.socialaccount.providers.fxa',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.hubic',
        'allauth.socialaccount.providers.instagram',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.linkedin_oauth2',
        'allauth.socialaccount.providers.odnoklassniki',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.persona',
        'allauth.socialaccount.providers.soundcloud',
        'allauth.socialaccount.providers.spotify',
        'allauth.socialaccount.providers.stackexchange',
        'allauth.socialaccount.providers.tumblr',
        'allauth.socialaccount.providers.twitch',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.vimeo',
        'allauth.socialaccount.providers.vk',
        'allauth.socialaccount.providers.weibo',
        'allauth.socialaccount.providers.xing',
        ...
    )

    SITE_ID = 1

urls.py::

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('allauth.urls')),
        ...
    )


Post-Installation
-----------------

In your Django root execute the command below to create your database tables::

    # Django 1.6 and below
    ./manage.py syncdb

    # Django 1.7 and above
    ./manage.py migrate

Now start your server, visit your admin pages (e.g. http://localhost:8000/admin/)
and follow these steps:

  1. Add a `Site` for your domain, matching `settings.SITE_ID` (`django.contrib.sites` app).
  2. For each OAuth based provider, add a `Social App` (`socialaccount` app).
  3. Fill in the site and the OAuth app credentials obtained from the provider.
