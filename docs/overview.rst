Overview
========

Requirements
------------

- Python 3.5, 3.6, 3.7, 3.8, 3.9, or 3.10

- Django (2.0+)

- python-openid or python3-openid (depending on your Python version)

- requests and requests-oauthlib

Supported Flows
---------------

- Signup of both local and social accounts

- Connecting more than one social account to a local account

- Disconnecting a social account -- requires setting a password if
  only the local account remains

- Optional instant-signup for social accounts -- no questions asked

- E-mail address management (multiple e-mail addresses, setting a primary)

- Password forgotten flow

- E-mail address verification flow

Supported Providers
-------------------

- 23andMe (OAuth2)

- 500px

- AgaveAPI (OAuth2)

- Amazon (OAuth2)

- Amazon Cognito (OAuth2)

- AngelList (OAuth2)

- Apple ("OAuth2")

- Asana (OAuth2)

- Auth0 (OAuth2)

- Authentiq (OAuth2)

- Azure (OAuth2)

- Baidu (OAuth2)

- Basecamp (OAuth2)

- Battle.net (OAuth2)

- Bitbucket (OAuth, OAuth2)

- Bitly (OAuth2)

- Box (OAuth2)

- CERN (OAuth2)

- CILogon (OAuth2)

- Clever (OAuth2)

- Coinbase (OAuth2)

- Dataporten (OAuth2)

- Daum (OAuth2)

- Digital Ocean (OAuth2)

- Discord (OAuth2)

- Disqus (OAuth2)

- Douban (OAuth2)

- Doximity (OAuth2)

- Draugiem

- Drip

- Dropbox (OAuth, OAuth2)

- Dwolla (OAuth2)

- Edmodo (OAuth2)

- Edx (open.edx.org) (OAuth2)

- Eve Online (OAuth2)

- Eventbrite (OAuth2)

- Evernote (OAuth)

- Exist (OAuth2)

- Facebook (both OAuth2 and JS SDK)

- Feedly (OAuth2)

- Figma (OAuth2)

- Firefox Accounts (OAuth2)

- Flickr (OAuth)

- FourSquare (OAuth2)

- Frontier (OAuth2)

- Gitea (OAuth2)

- Github (OAuth2)

- GitLab (OAuth2)

- Globus (OAuth2)

- Google (OAuth2)

- Gumroad (OAuth2)

- Hubic (OAuth2)

- Hubspot (OAuth2)

- Instagram (OAuth2)

- JupyterHub (OAuth2)

- Kakao (OAuth2)

- Keycloak (OAuth2)

- LemonLDAP::NG (OAuth2)

- Line (OAuth2)

- LinkedIn (OAuth, OAuth2)

- Mail.Ru (OAuth2)

- MailChimp (OAuth2)

- MediaWiki (OAuth2)

- Meetup (OAuth2)

- Microsoft (Graph) (OAuth2)

- Naver (OAuth2)

- NetIQ/Microfocus AccessManager (OAuth2)

- NextCloud (OAuth2)

- Odnoklassniki (OAuth2)

- Okta (OAuth2)

- OpenId

- OpenStreetMap (OAuth)

- ORCID (OAuth2)

- Patreon (OAuth2)

- Paypal (OAuth2)

- Persona

- Pinterest (OAuth2)

- Pocket (OAuth)

- QuickBooks (OAuth2)

- Reddit (OAuth2)

- Robinhood (OAuth2)

- Salesforce (OAuth2)

- ShareFile (OAuth2)

- Shopify (OAuth2)

- Slack (OAuth2)

- Snapchat (OAuth2)

- SoundCloud (OAuth2)

- Spotify (OAuth2)

- Stack Exchange (OAuth2)

- Steam (OpenID)

- Stocktwits (OAuth2)

- Strava (OAuth2)

- Stripe (OAuth2)

- Telegram

- TrainingPeaks (OAuth2)

- Trello (OAuth)

- Tumblr (OAuth)

- Twitch (OAuth2)

- Twitter (OAuth)

- Untappd (OAuth2)

- Vimeo (OAuth, OAuth2)

- VK (OAuth2)

- Weibo (OAuth2)

- Weixin (OAuth2)

- Windows Live (OAuth2)

- Xing (OAuth)

- Yahoo (OAuth2)

- Yandex (OAuth2)

- YNAB (OAuth2)

- Zoho (Oauth2)

- Zoom (OAuth2)

- Feishu (OAuth2)


Note: OAuth/OAuth2 support is built using a common code base, making it easy to add support for additional OAuth/OAuth2 providers. More will follow soon...


Features
--------

- Supports multiple authentication schemes (e.g. login by user name,
  or by e-mail), as well as multiple strategies for account
  verification (ranging from none to e-mail verification).

- All access tokens are consistently stored so that you can publish
  wall updates etc.

Architecture & Design
---------------------

- Pluggable signup form for asking additional questions during signup.

- Support for connecting multiple social accounts to a Django user account.

- The required consumer keys and secrets for interacting with
  Facebook, Twitter and the likes are to be configured in the database
  via the Django admin using the SocialApp model.

- Consumer keys, tokens make use of the Django sites framework. This
  is especially helpful for larger multi-domain projects, but also
  allows for easy switching between a development (localhost) and
  production setup without messing with your settings and database.
