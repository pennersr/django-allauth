from pathlib import Path

from django.contrib.auth.hashers import PBKDF2PasswordHasher


SECRET_KEY = "psst"
SITE_ID = 1
ALLOWED_HOSTS = (
    "testserver",
    "example.com",
)
USE_I18N = False
USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

ROOT_URLCONF = "tests.headless_only.urls"
LOGIN_URL = "/login/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            Path(__file__).parent.parent
            / "examples"
            / "regular-django"
            / "example"
            / "templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.agave_provider",
    "allauth.socialaccount.providers.amazon_provider",
    "allauth.socialaccount.providers.amazon_cognito_provider",
    "allauth.socialaccount.providers.angellist_provider",
    "allauth.socialaccount.providers.apple_provider",
    "allauth.socialaccount.providers.asana_provider",
    "allauth.socialaccount.providers.atlassian_provider",
    "allauth.socialaccount.providers.auth0_provider",
    "allauth.socialaccount.providers.authentiq_provider",
    "allauth.socialaccount.providers.baidu_provider",
    "allauth.socialaccount.providers.basecamp_provider",
    "allauth.socialaccount.providers.battlenet_provider",
    "allauth.socialaccount.providers.bitbucket_oauth2_provider",
    "allauth.socialaccount.providers.bitly_provider",
    "allauth.socialaccount.providers.box_provider",
    "allauth.socialaccount.providers.cilogon_provider",
    "allauth.socialaccount.providers.clever_provider",
    "allauth.socialaccount.providers.coinbase_provider",
    "allauth.socialaccount.providers.dataporten_provider",
    "allauth.socialaccount.providers.daum_provider",
    "allauth.socialaccount.providers.digitalocean_provider",
    "allauth.socialaccount.providers.dingtalk_provider",
    "allauth.socialaccount.providers.discord_provider",
    "allauth.socialaccount.providers.disqus_provider",
    "allauth.socialaccount.providers.douban_provider",
    "allauth.socialaccount.providers.doximity_provider",
    "allauth.socialaccount.providers.draugiem_provider",
    "allauth.socialaccount.providers.drip_provider",
    "allauth.socialaccount.providers.dropbox_provider",
    "allauth.socialaccount.providers.dummy_provider",
    "allauth.socialaccount.providers.dwolla_provider",
    "allauth.socialaccount.providers.edmodo_provider",
    "allauth.socialaccount.providers.edx_provider",
    "allauth.socialaccount.providers.eventbrite_provider",
    "allauth.socialaccount.providers.eveonline_provider",
    "allauth.socialaccount.providers.evernote_provider",
    "allauth.socialaccount.providers.exist_provider",
    "allauth.socialaccount.providers.facebook_provider",
    "allauth.socialaccount.providers.feedly_provider",
    "allauth.socialaccount.providers.figma_provider",
    "allauth.socialaccount.providers.fivehundredpx_provider",
    "allauth.socialaccount.providers.flickr_provider",
    "allauth.socialaccount.providers.foursquare_provider",
    "allauth.socialaccount.providers.frontier_provider",
    "allauth.socialaccount.providers.fxa_provider",
    "allauth.socialaccount.providers.gitea_provider",
    "allauth.socialaccount.providers.github_provider",
    "allauth.socialaccount.providers.gitlab_provider",
    "allauth.socialaccount.providers.globus_provider",
    "allauth.socialaccount.providers.google_provider",
    "allauth.socialaccount.providers.gumroad_provider",
    "allauth.socialaccount.providers.hubic_provider",
    "allauth.socialaccount.providers.hubspot_provider",
    "allauth.socialaccount.providers.instagram_provider",
    "allauth.socialaccount.providers.jupyterhub_provider",
    "allauth.socialaccount.providers.kakao_provider",
    "allauth.socialaccount.providers.lemonldap_provider",
    "allauth.socialaccount.providers.line_provider",
    "allauth.socialaccount.providers.linkedin_oauth2_provider",
    "allauth.socialaccount.providers.mailchimp_provider",
    "allauth.socialaccount.providers.mailru_provider",
    "allauth.socialaccount.providers.mediawiki_provider",
    "allauth.socialaccount.providers.meetup_provider",
    "allauth.socialaccount.providers.microsoft_provider",
    "allauth.socialaccount.providers.miro_provider",
    "allauth.socialaccount.providers.naver_provider",
    "allauth.socialaccount.providers.netiq_provider",
    "allauth.socialaccount.providers.nextcloud_provider",
    "allauth.socialaccount.providers.notion_provider",
    "allauth.socialaccount.providers.odnoklassniki_provider",
    "allauth.socialaccount.providers.openid_provider",
    "allauth.socialaccount.providers.openid_connect_provider",
    "allauth.socialaccount.providers.openstreetmap_provider",
    "allauth.socialaccount.providers.orcid_provider",
    "allauth.socialaccount.providers.patreon_provider",
    "allauth.socialaccount.providers.paypal_provider",
    "allauth.socialaccount.providers.pinterest_provider",
    "allauth.socialaccount.providers.pocket_provider",
    "allauth.socialaccount.providers.questrade_provider",
    "allauth.socialaccount.providers.quickbooks_provider",
    "allauth.socialaccount.providers.reddit_provider",
    "allauth.socialaccount.providers.robinhood_provider",
    "allauth.socialaccount.providers.salesforce_provider",
    "allauth.socialaccount.providers.saml_provider",
    "allauth.socialaccount.providers.sharefile_provider",
    "allauth.socialaccount.providers.shopify_provider",
    "allauth.socialaccount.providers.slack_provider",
    "allauth.socialaccount.providers.snapchat_provider",
    "allauth.socialaccount.providers.soundcloud_provider",
    "allauth.socialaccount.providers.spotify_provider",
    "allauth.socialaccount.providers.stackexchange_provider",
    "allauth.socialaccount.providers.steam_provider",
    "allauth.socialaccount.providers.stocktwits_provider",
    "allauth.socialaccount.providers.strava_provider",
    "allauth.socialaccount.providers.stripe_provider",
    "allauth.socialaccount.providers.telegram_provider",
    "allauth.socialaccount.providers.trainingpeaks_provider",
    "allauth.socialaccount.providers.trello_provider",
    "allauth.socialaccount.providers.tumblr_provider",
    "allauth.socialaccount.providers.twentythreeandme_provider",
    "allauth.socialaccount.providers.twitch_provider",
    "allauth.socialaccount.providers.twitter_provider",
    "allauth.socialaccount.providers.twitter_oauth2_provider",
    "allauth.socialaccount.providers.untappd_provider",
    "allauth.socialaccount.providers.vimeo_provider",
    "allauth.socialaccount.providers.vimeo_oauth2_provider",
    "allauth.socialaccount.providers.vk_provider",
    "allauth.socialaccount.providers.wahoo_provider",
    "allauth.socialaccount.providers.weibo_provider",
    "allauth.socialaccount.providers.weixin_provider",
    "allauth.socialaccount.providers.windowslive_provider",
    "allauth.socialaccount.providers.xing_provider",
    "allauth.socialaccount.providers.yahoo_provider",
    "allauth.socialaccount.providers.yandex_provider",
    "allauth.socialaccount.providers.ynab_provider",
    "allauth.socialaccount.providers.zoho_provider",
    "allauth.socialaccount.providers.zoom_provider",
    "allauth.socialaccount.providers.okta_provider",
    "allauth.socialaccount.providers.feishu_provider",
    "allauth.usersessions",
    "allauth.headless",
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

STATIC_ROOT = "/tmp/"  # Dummy
STATIC_URL = "/static/"


class MyPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    """
    A subclass of PBKDF2PasswordHasher that uses 1 iteration.

    This is for test purposes only. Never use anywhere else.
    """

    iterations = 1


PASSWORD_HASHERS = [
    "tests.headless_only.settings.MyPBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "unittest-server",
                "name": "Unittest Server",
                "client_id": "Unittest client_id",
                "client_secret": "Unittest client_secret",
                "settings": {
                    "server_url": "https://unittest.example.com",
                },
            },
            {
                "provider_id": "other-server",
                "name": "Other Example Server",
                "client_id": "other client_id",
                "client_secret": "other client_secret",
                "settings": {
                    "server_url": "https://other.example.com",
                },
            },
        ],
    }
}

ACCOUNT_LOGIN_BY_CODE_ENABLED = True

HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/spa/confirm-email?key={key}",
    "account_reset_password": "/spa/password/reset/",
    "account_reset_password_from_key": "/spa/password/reset/{key}/",
    "account_signup": "/spa/signup",
}
