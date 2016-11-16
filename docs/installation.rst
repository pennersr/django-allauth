Installation
============

Django
------

Python package::

    pip install django-allauth

settings.py (Important - Please note 'django.contrib.sites' is required as INSTALLED_APPS)::

    # For Django 1.7, use:
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        # Required by `allauth` template tags
        'django.core.context_processors.request',
        ...
    )

    # If you are running Django 1.8+, specify the context processors
    # as follows:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # Already defined Django-related contexts here

                    # `allauth` needs this from django
                    'django.template.context_processors.request',
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
        'allauth.socialaccount.providers.asana',
        'allauth.socialaccount.providers.baidu',
        'allauth.socialaccount.providers.basecamp',
        'allauth.socialaccount.providers.bitbucket',
        'allauth.socialaccount.providers.bitbucket_oauth2',
        'allauth.socialaccount.providers.bitly',
        'allauth.socialaccount.providers.coinbase',
        'allauth.socialaccount.providers.digitalocean',
        'allauth.socialaccount.providers.douban',
        'allauth.socialaccount.providers.draugiem',
        'allauth.socialaccount.providers.dropbox',
        'allauth.socialaccount.providers.dropbox_oauth2',
        'allauth.socialaccount.providers.edmodo',
        'allauth.socialaccount.providers.eveonline',
        'allauth.socialaccount.providers.evernote',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.feedly',
        'allauth.socialaccount.providers.flickr',
        'allauth.socialaccount.providers.foursquare',
        'allauth.socialaccount.providers.fxa',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.gitlab',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.hubic',
        'allauth.socialaccount.providers.instagram',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.linkedin_oauth2',
        'allauth.socialaccount.providers.mailru',
        'allauth.socialaccount.providers.odnoklassniki',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.orcid',
        'allauth.socialaccount.providers.paypal',
        'allauth.socialaccount.providers.persona',
        'allauth.socialaccount.providers.pinterest',
        'allauth.socialaccount.providers.reddit',
        'allauth.socialaccount.providers.robinhood',
        'allauth.socialaccount.providers.shopify',
        'allauth.socialaccount.providers.slack',
        'allauth.socialaccount.providers.soundcloud',
        'allauth.socialaccount.providers.spotify',
        'allauth.socialaccount.providers.stackexchange',
        'allauth.socialaccount.providers.stripe',
        'allauth.socialaccount.providers.tumblr',
        'allauth.socialaccount.providers.twentythreeandme',
        'allauth.socialaccount.providers.twitch',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.untappd',
        'allauth.socialaccount.providers.vimeo',
        'allauth.socialaccount.providers.vk',
        'allauth.socialaccount.providers.weibo',
        'allauth.socialaccount.providers.weixin',
        'allauth.socialaccount.providers.windowslive',
        'allauth.socialaccount.providers.xing',
        ...
    )

    SITE_ID = 1

urls.py::

    urlpatterns = [
        ...
        url(r'^accounts/', include('allauth.urls')),
        ...
    ]


Post-Installation
-----------------

In your Django root execute the command below to create your database tables::

    ./manage.py migrate

Now start your server, visit your admin pages (e.g. http://localhost:8000/admin/)
and follow these steps:

1. Add a `Site` for your domain, matching `settings.SITE_ID` (`django.contrib.sites` app).
2. For each OAuth based provider, add a `Social App` (`socialaccount` app).
3. Fill in the site and the OAuth app credentials obtained from the provider.

More detailed description:
   Add a Site through the admin panel. Since I am developing on my machine, I've set up my site with the "Domain Name" field set as "127.0.0.1:8000" and the "Display Name" shouldn't matter.

    Your SITE_ID in settings.py needs to match the actual database ID from the Site you added through the admin panel. To do this you can go to the details of the Site you created through the admin panel and look at the url for the ID number. Mine ended up being "5"(I recreated several sites trying to get this to work).

    Create a Social Application through the admin panel. This is pretty easy as you only need to setup an Application through the provider (e.g. create a Facebook app on Facebooks website) and use the secret code and app ID they give you to fill out the django form. Be sure to add the django Site you created in step 1 to the Social Application you are making in this step.
