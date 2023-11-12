Quickstart
==========

First, Install the python package::

    pip install django-allauth

Then, assuming you have a Django project up and running, add the following to
the ``settings.py`` of your project::

    # Specify the context processors as follows:
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

    AUTHENTICATION_BACKENDS = [
        ...
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',

        # `allauth` specific authentication methods, such as login by email
        'allauth.account.auth_backends.AuthenticationBackend',
        ...
    ]

    INSTALLED_APPS = [
        ...
        # The following apps are required:
        'django.contrib.auth',
        'django.contrib.messages',

        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # ... include the providers you want to enable:
        'allauth.socialaccount.providers.agave',
        'allauth.socialaccount.providers.amazon',
        'allauth.socialaccount.providers.amazon_cognito',
        'allauth.socialaccount.providers.angellist',
        'allauth.socialaccount.providers.apple',
        'allauth.socialaccount.providers.asana',
        'allauth.socialaccount.providers.auth0',
        'allauth.socialaccount.providers.authentiq',
        'allauth.socialaccount.providers.baidu',
        'allauth.socialaccount.providers.basecamp',
        'allauth.socialaccount.providers.battlenet',
        'allauth.socialaccount.providers.bitbucket',
        'allauth.socialaccount.providers.bitbucket_oauth2',
        'allauth.socialaccount.providers.bitly',
        'allauth.socialaccount.providers.box',
        'allauth.socialaccount.providers.cilogon',
        'allauth.socialaccount.providers.clever',
        'allauth.socialaccount.providers.coinbase',
        'allauth.socialaccount.providers.dataporten',
        'allauth.socialaccount.providers.daum',
        'allauth.socialaccount.providers.digitalocean',
        'allauth.socialaccount.providers.dingtalk',
        'allauth.socialaccount.providers.discord',
        'allauth.socialaccount.providers.disqus',
        'allauth.socialaccount.providers.douban',
        'allauth.socialaccount.providers.doximity',
        'allauth.socialaccount.providers.draugiem',
        'allauth.socialaccount.providers.drip',
        'allauth.socialaccount.providers.dropbox',
        'allauth.socialaccount.providers.dwolla',
        'allauth.socialaccount.providers.edmodo',
        'allauth.socialaccount.providers.edx',
        'allauth.socialaccount.providers.eventbrite',
        'allauth.socialaccount.providers.eveonline',
        'allauth.socialaccount.providers.evernote',
        'allauth.socialaccount.providers.exist',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.feedly',
        'allauth.socialaccount.providers.figma',
        'allauth.socialaccount.providers.fivehundredpx',
        'allauth.socialaccount.providers.flickr',
        'allauth.socialaccount.providers.foursquare',
        'allauth.socialaccount.providers.frontier',
        'allauth.socialaccount.providers.fxa',
        'allauth.socialaccount.providers.gitea',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.gitlab',
        'allauth.socialaccount.providers.globus',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.gumroad',
        'allauth.socialaccount.providers.hubic',
        'allauth.socialaccount.providers.instagram',
        'allauth.socialaccount.providers.jupyterhub',
        'allauth.socialaccount.providers.kakao',
        'allauth.socialaccount.providers.lemonldap',
        'allauth.socialaccount.providers.line',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.linkedin_oauth2',
        'allauth.socialaccount.providers.mailchimp',
        'allauth.socialaccount.providers.mailru',
        'allauth.socialaccount.providers.mediawiki',
        'allauth.socialaccount.providers.meetup',
        'allauth.socialaccount.providers.miro',
        'allauth.socialaccount.providers.microsoft',
        'allauth.socialaccount.providers.naver',
        'allauth.socialaccount.providers.nextcloud',
        'allauth.socialaccount.providers.notion',
        'allauth.socialaccount.providers.odnoklassniki',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.openid_connect',
        'allauth.socialaccount.providers.openstreetmap',
        'allauth.socialaccount.providers.orcid',
        'allauth.socialaccount.providers.patreon',
        'allauth.socialaccount.providers.paypal',
        'allauth.socialaccount.providers.persona',
        'allauth.socialaccount.providers.pinterest',
        'allauth.socialaccount.providers.pocket',
        "allauth.socialaccount.providers.questrade",
        'allauth.socialaccount.providers.quickbooks',
        'allauth.socialaccount.providers.reddit',
        'allauth.socialaccount.providers.robinhood',
        'allauth.socialaccount.providers.salesforce',
        'allauth.socialaccount.providers.sharefile',
        'allauth.socialaccount.providers.shopify',
        'allauth.socialaccount.providers.slack',
        'allauth.socialaccount.providers.snapchat',
        'allauth.socialaccount.providers.soundcloud',
        'allauth.socialaccount.providers.spotify',
        'allauth.socialaccount.providers.stackexchange',
        'allauth.socialaccount.providers.steam',
        'allauth.socialaccount.providers.stocktwits',
        'allauth.socialaccount.providers.strava',
        'allauth.socialaccount.providers.stripe',
        'allauth.socialaccount.providers.telegram',
        'allauth.socialaccount.providers.trainingpeaks',
        'allauth.socialaccount.providers.trello',
        'allauth.socialaccount.providers.tumblr',
        'allauth.socialaccount.providers.twentythreeandme',
        'allauth.socialaccount.providers.twitch',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.twitter_oauth2',
        'allauth.socialaccount.providers.untappd',
        'allauth.socialaccount.providers.vimeo',
        'allauth.socialaccount.providers.vimeo_oauth2',
        'allauth.socialaccount.providers.vk',
        'allauth.socialaccount.providers.wahoo',
        'allauth.socialaccount.providers.weibo',
        'allauth.socialaccount.providers.weixin',
        'allauth.socialaccount.providers.windowslive',
        'allauth.socialaccount.providers.xing',
        'allauth.socialaccount.providers.yahoo',
        'allauth.socialaccount.providers.yandex',
        'allauth.socialaccount.providers.ynab',
        'allauth.socialaccount.providers.zoho',
        'allauth.socialaccount.providers.zoom',
        'allauth.socialaccount.providers.okta',
        'allauth.socialaccount.providers.feishu',
        ...
    ]

    MIDDLEWARE = (
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",

        # Add the account middleware:
        "allauth.account.middleware.AccountMiddleware",
    )

    # Provider specific settings
    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            # For each OAuth based provider, either add a ``SocialApp``
            # (``socialaccount`` app) containing the required client
            # credentials, or list them here:
            'APP': {
                'client_id': '123',
                'secret': '456',
                'key': ''
            }
        }
    }

Additionally, add this to your project ``urls.py``::

    urlpatterns = [
        ...
        path('accounts/', include('allauth.urls')),
        ...
    ]

Note that you do not necessarily need the URLs provided by
``django.contrib.auth.urls``. Instead of the URLs ``login``, ``logout``, and
``password_change`` (among others), you can use the URLs provided by
``allauth``: ``account_login``, ``account_logout``, ``account_set_password``...


Post-Installation
-----------------

In your Django root execute the command below to create your database tables::

    python manage.py migrate

Now start your server, visit your admin pages (e.g. http://localhost:8000/admin/)
and follow these steps:

- For each OAuth based provider, either add a ``SocialApp`` (``socialaccount``
  app) containing the required client credentials, or, make sure that these are
  configured via the ``SOCIALACCOUNT_PROVIDERS[<provider>]['APP']`` setting (see example above).
