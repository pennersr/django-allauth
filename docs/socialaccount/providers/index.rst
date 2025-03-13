Providers
=========

Introduction
************

Most providers require you to sign up for a so called API client or app,
containing a client ID and API secret. You must add a ``SocialApp``
record per provider via the Django admin containing these app
credentials.

When creating the OAuth app on the side of the provider pay special
attention to the callback URL (sometimes also referred to as redirect
URL). If you do not configure this correctly, you will receive login
failures when attempting to log in, such as::

    An error occurred while attempting to login via your social network account.

Use a callback URL of the form::

    http://example.com/accounts/twitter/login/callback/
    http://example.com/accounts/soundcloud/login/callback/
    ...

For local development, use the following::

    http://127.0.0.1:8000/accounts/twitter/login/callback/


Provider Specifics
******************

.. toctree::
   :maxdepth: 1

   23andme
   500px
   agave
   amazon_cognito
   amazon
   angellist
   apple
   atlassian
   auth0
   authelia
   authentiq
   baidu
   basecamp
   battlenet
   bitbucket
   box
   cern
   cilogon
   clever
   dataporten
   daum
   digitalocean
   dingtalk
   discord
   doximity
   draugiem
   drip
   dropbox
   dwolla
   edmodo
   edx
   eventbrite
   eveonline
   evernote
   exist
   facebook
   feishu
   figma
   flickr
   frontier
   fxa
   gitea
   github
   gitlab
   globus
   google
   gumroad
   hubspot
   instagram
   jupyterhub
   kakao
   keycloak
   lemonldap
   lichess
   line
   linkedin
   mailchimp
   mediawiki
   microsoft
   miro
   naver
   netiq
   nextcloud
   notion
   odnoklassniki
   okta
   openid_connect
   openid
   openstreetmap
   orcid
   patreon
   paypal
   pinterest
   pocket
   questrade
   quickbooks
   reddit
   saml
   salesforce
   sharefile
   shopify
   slack
   snapchat
   soundcloud
   stackexchange
   steam
   stocktwits
   strava
   stripe
   telegram
   tiktok
   trainingpeaks
   trello
   tumblr_oauth2
   twitch
   twitter_oauth2
   twitter
   untappd
   vimeo_oauth2
   vimeo
   wahoo
   weibo
   weixin
   windowslive
   xing
   yahoo
   yandex
   ynab
   zoho
   zoom
