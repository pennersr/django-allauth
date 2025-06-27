from pathlib import Path
from typing import Tuple


INSTALLED_SOCIALACCOUNT_APPS: Tuple[str, ...] = (
    "allauth.socialaccount",
    "allauth.socialaccount.providers.agave",
    "allauth.socialaccount.providers.amazon",
    "allauth.socialaccount.providers.amazon_cognito",
    "allauth.socialaccount.providers.angellist",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.asana",
    "allauth.socialaccount.providers.atlassian",
    "allauth.socialaccount.providers.auth0",
    "allauth.socialaccount.providers.authentiq",
    "allauth.socialaccount.providers.baidu",
    "allauth.socialaccount.providers.basecamp",
    "allauth.socialaccount.providers.battlenet",
    "allauth.socialaccount.providers.bitbucket_oauth2",
    "allauth.socialaccount.providers.bitly",
    "allauth.socialaccount.providers.box",
    "allauth.socialaccount.providers.cilogon",
    "allauth.socialaccount.providers.clever",
    "allauth.socialaccount.providers.coinbase",
    "allauth.socialaccount.providers.dataporten",
    "allauth.socialaccount.providers.daum",
    "allauth.socialaccount.providers.digitalocean",
    "allauth.socialaccount.providers.dingtalk",
    "allauth.socialaccount.providers.discord",
    "allauth.socialaccount.providers.disqus",
    "allauth.socialaccount.providers.douban",
    "allauth.socialaccount.providers.doximity",
    "allauth.socialaccount.providers.draugiem",
    "allauth.socialaccount.providers.drip",
    "allauth.socialaccount.providers.dropbox",
    "allauth.socialaccount.providers.dummy",
    "allauth.socialaccount.providers.dwolla",
    "allauth.socialaccount.providers.edmodo",
    "allauth.socialaccount.providers.edx",
    "allauth.socialaccount.providers.eventbrite",
    "allauth.socialaccount.providers.eveonline",
    "allauth.socialaccount.providers.evernote",
    "allauth.socialaccount.providers.exist",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.feedly",
    "allauth.socialaccount.providers.feishu",
    "allauth.socialaccount.providers.figma",
    "allauth.socialaccount.providers.fivehundredpx",
    "allauth.socialaccount.providers.flickr",
    "allauth.socialaccount.providers.foursquare",
    "allauth.socialaccount.providers.frontier",
    "allauth.socialaccount.providers.fxa",
    "allauth.socialaccount.providers.gitea",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.gitlab",
    "allauth.socialaccount.providers.globus",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.gumroad",
    "allauth.socialaccount.providers.hubic",
    "allauth.socialaccount.providers.hubspot",
    "allauth.socialaccount.providers.instagram",
    "allauth.socialaccount.providers.jupyterhub",
    "allauth.socialaccount.providers.kakao",
    "allauth.socialaccount.providers.lemonldap",
    "allauth.socialaccount.providers.lichess",
    "allauth.socialaccount.providers.line",
    "allauth.socialaccount.providers.linkedin_oauth2",
    "allauth.socialaccount.providers.mailchimp",
    "allauth.socialaccount.providers.mailcow",
    "allauth.socialaccount.providers.mailru",
    "allauth.socialaccount.providers.mediawiki",
    "allauth.socialaccount.providers.meetup",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.miro",
    "allauth.socialaccount.providers.naver",
    "allauth.socialaccount.providers.netiq",
    "allauth.socialaccount.providers.nextcloud",
    "allauth.socialaccount.providers.notion",
    "allauth.socialaccount.providers.odnoklassniki",
    "allauth.socialaccount.providers.okta",
    "allauth.socialaccount.providers.openid",
    "allauth.socialaccount.providers.openid_connect",
    "allauth.socialaccount.providers.openstreetmap",
    "allauth.socialaccount.providers.orcid",
    "allauth.socialaccount.providers.patreon",
    "allauth.socialaccount.providers.paypal",
    "allauth.socialaccount.providers.pinterest",
    "allauth.socialaccount.providers.pocket",
    "allauth.socialaccount.providers.questrade",
    "allauth.socialaccount.providers.quickbooks",
    "allauth.socialaccount.providers.reddit",
    "allauth.socialaccount.providers.robinhood",
    "allauth.socialaccount.providers.salesforce",
    "allauth.socialaccount.providers.sharefile",
    "allauth.socialaccount.providers.shopify",
    "allauth.socialaccount.providers.slack",
    "allauth.socialaccount.providers.snapchat",
    "allauth.socialaccount.providers.soundcloud",
    "allauth.socialaccount.providers.spotify",
    "allauth.socialaccount.providers.stackexchange",
    "allauth.socialaccount.providers.steam",
    "allauth.socialaccount.providers.stocktwits",
    "allauth.socialaccount.providers.strava",
    "allauth.socialaccount.providers.stripe",
    "allauth.socialaccount.providers.telegram",
    "allauth.socialaccount.providers.tiktok",
    "allauth.socialaccount.providers.trainingpeaks",
    "allauth.socialaccount.providers.trello",
    "allauth.socialaccount.providers.tumblr",
    "allauth.socialaccount.providers.tumblr_oauth2",
    "allauth.socialaccount.providers.twentythreeandme",
    "allauth.socialaccount.providers.twitch",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.twitter_oauth2",
    "allauth.socialaccount.providers.untappd",
    "allauth.socialaccount.providers.vimeo",
    "allauth.socialaccount.providers.vimeo_oauth2",
    "allauth.socialaccount.providers.vk",
    "allauth.socialaccount.providers.wahoo",
    "allauth.socialaccount.providers.weibo",
    "allauth.socialaccount.providers.weixin",
    "allauth.socialaccount.providers.windowslive",
    "allauth.socialaccount.providers.xing",
    "allauth.socialaccount.providers.yahoo",
    "allauth.socialaccount.providers.yandex",
    "allauth.socialaccount.providers.ynab",
    "allauth.socialaccount.providers.zoho",
    "allauth.socialaccount.providers.zoom",
)

# Instaling the necessary dependencies for testing SAML slows the CI pipeline
# down considerably, as we need to:
#
#     pip install --no-binary xmlsec --no-binary lxml {opts} {packages}
#
# Also see: https://github.com/xmlsec/python-xmlsec/issues/320#issuecomment-2129076807
try:
    import onelogin  # noqa

    INSTALLED_SOCIALACCOUNT_APPS += ("allauth.socialaccount.providers.saml",)
except ImportError:
    pass


IDP_OIDC_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDAvGhvhFJkUwEa
jq48SQ2rWHxPC/kbG9lJb0cl6qjaLA27atC/aCdmnlMnnng7PrjfOLtPatXjuKk3
S8wpIqB74wuzEnBs+/3BaqylxN1pkazRv+w0i26B7igLQVjsUXkz/icSPoSkZSxO
MB4vbGfwnbyUOqHaWumnDwXOZ4FKrxxXMSJcJVF141MaqANh90Wwsx7PK/Nb8hkj
blKcbfSn9x5Q7jRN2e1yfC6xtsrR+q5o26m0H2uXiFaWtxH6GPKnsgA90RmIblQ7
nYmg39C01Xli0z5ehzd5oAGpXEDP9uO9+1kVWor8TETl7vpaVqnauLx/tTl09qEM
WpX6VmFVAgMBAAECggEAEdPbnSUSMfFzkq9L8ouXVhgTN4SWACntSVufqyQvhi64
/nL86BeMPXO7oViJKoG8u/kVal0pd6znChRayBtJ2OvBc0jrWUldyXxCh/rTuCYf
ZC9qe9nB2QbccV4UCZfnrCWAG7HotwQcuwa8ZAqU+q68eMGLoxTxs+Ax20u7q9qp
Y+QNNZOuH+1pC8l+0CaTTpFa1sty+/xnGtM6UgaLVQ7E4ZvFRWyWfIAzWFzFfFWW
oVK7mYD8uVPMEpHPPlaNj+0C7LNM1NUpg/ifKPYl13OnhQr2WMji35LwrEsK0lpr
tXw6wm7rl9NbXC93hpW9V252KNuL3LbN9lLAICSOAQKBgQD24BY4dCRErTZY8+Zp
fBf+2h6RPHtukTFsyMdC903R4ZuLGSoteKTesAte2CfsG5YvgXx/eZHGRvnPBF7A
Pjb/ZJnk3HzsHirivZ19xvd5MVQRobUXmh42gJW5V5XixqMjBfpoWcOL5H1ly9m+
2EZKeh7B8wNXTj/dCoOmNbF3QQKBgQDH3A8gkWT6udSMTVT1oxb1ifJUTWtwdfrn
rZQtk1ov962sXwMqglt9sdt9+9gajF7LzxLxStRUY16U0QUMjfHVQiQQfzfnI2a7
r2dg1g03msDg7QRVD/NHuzkQL37zeQQalrqTCbq43/CFbJDlGkr9xqNfAICya4Vp
gJW2zdJZFQKBgQCcS4Rl20m23P5iVI+USscaRtdBVcxDVNK4r2hPwifXb4C9EIJ+
ZTnj7gpU0n574X80tkKupbWflQHEiVy/UuQYzoULunewOO0nvan+nj/Az3UM8Jao
yZ7FHKUtwQCYoO9ZVgiRlfrSDydAkk1ZoKznq+bbHVIJLPYLqANu7+FZwQKBgQCn
Oq35rU7WMGn137soMgfC+mMnQQSWPFHuSyKCpBpBqrfKVFH83siZOxoSp4kiZbPo
S2NpPRi/Z8o7MU5NO/RPYiF1IE3xfIC4qMMSlujGTxn22rvWRRtmOPU9YtCR/v99
FAQXhnuTt+W0bqwq1z5KbExE8NG++RLPvYUISd4pJQKBgGxyMWgE2AeILIcrw/Ts
zM1ct2vV7Iet8eVRPUAzESQu0aGBm7Eho9+mh3vUJtlStChJIvCT+lbEgXmsDGMk
HxD4lATnNILRfRTdPgu8IYS3/A4LoXjjhsPmx8NQ6PwnKnseFtQMBKQsX2HVfMVP
vOZ+KpqzUW/vig+SalRbQMIR
-----END PRIVATE KEY-----
"""


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(__file__).parent / "templates"],
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
