Overview
========

Requirements
------------

- Python 2.6, 2.7 or 3.3

- Django (1.4.3+)

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

- Amazon (OAuth2)

- AngelList (OAuth2)

- Bitbucket (OAuth)

- Bitly (OAuth2)

- Dropbox (OAuth)

- Facebook (both OAuth2 and JS SDK)

- Feedly (OAuth2)

- Flickr (OAuth)

- Github (OAuth2)

- Google (OAuth2)

- Hubic (OAuth2)

- Instagram (OAuth2)

- LinkedIn (OAuth, OAuth2)

- Mail.Ru (OAuth2)

- OpenId

- ORCID (OAuth2)

- Paypal (OAuth2)

- Persona

- SoundCloud (OAuth2)

- Stack Exchange (OAuth2)

- Tumblr (OAuth)

- Twitch (OAuth2)

- Twitter (OAuth)

- Vimeo (OAuth)

- VK (OAuth2)

- Weibo (OAuth2)

- Windows Live (OAuth2)

- Xing (OAuth)


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
  allows for for easy switching between a development (localhost) and
  production setup without messing with your settings and database.
