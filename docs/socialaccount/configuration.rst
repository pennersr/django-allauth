Configuration
=============

Available settings:

``SOCIALACCOUNT_ADAPTER`` (default: ``"allauth.socialaccount.adapter.DefaultSocialAccountAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

``SOCIALACCOUNT_AUTO_SIGNUP`` (default: ``True``)
  Attempt to bypass the signup form by using fields (e.g. username,
  email) retrieved from the social account provider. If a conflict
  arises due to a duplicate email address the signup form will still
  kick in.

``SOCIALACCOUNT_EMAIL_AUTHENTICATION`` (default: ``False``)
  Consider a scenario where a social login occurs, and the social account comes
  with a verified email address (verified by the account provider), but that
  email address is already taken by a local user account. Additionally, assume
  that the local user account does not have any social account connected. Now,
  if the provider can be fully trusted, you can argue that we should treat this
  scenario as a login to the existing local user account even if the local
  account does not already have the social account connected, because --
  according to the provider -- the user logging in has ownership of the email
  address.  This is how this scenario is handled when
  ``SOCIALACCOUNT_EMAIL_AUTHENTICATION`` is set to ``True``. As this implies
  that an untrustworthy provider can login to any local account by fabricating
  social account data, this setting defaults to ``False``. Only set it to
  ``True`` if you are using providers that can be fully trusted. Instead of
  turning this on globally, you can also turn it on selectively per provider,
  for example::

      SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'EMAIL_AUTHENTICATION': True
        }
      }


``SOCIALACCOUNT_EMAIL_VERIFICATION`` (default: ``ACCOUNT_EMAIL_VERIFICATION``)
  As ``ACCOUNT_EMAIL_VERIFICATION``, but for social accounts.

``SOCIALACCOUNT_EMAIL_REQUIRED`` (default: ``ACCOUNT_EMAIL_REQUIRED``)
  The user is required to hand over an email address when signing up
  using a social account.

``SOCIALACCOUNT_FORMS``
  Used to override forms. Defaults to::

    SOCIALACCOUNT_FORMS = {
        'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
        'signup': 'allauth.socialaccount.forms.SignupForm',
    }

``SOCIALACCOUNT_LOGIN_ON_GET`` (default: ``False``)
  Controls whether or not the endpoints for initiating a social login (for
  example, "/accounts/google/login/") require a POST request to initiate the
  handshake. For security considerations, it is strongly recommended to
  require POST requests.

``SOCIALACCOUNT_PROVIDERS`` (default: ``{}``)
  Dictionary containing provider specific settings.

  The 'APP' section for each provider is generic to all providers and
  can also be specified in the database using a ``SocialApp`` model
  instance instead of here. All other sections are provider-specific and
  are documented in the `for each provider separately
  <providers.html>`__.

  Example::

    SOCIALACCOUNT_PROVIDERS = {
        "github": {
            # For each provider, you can choose whether or not the
            # email address(es) retrieved from the provider are to be
            # interpreted as verified.
            "VERIFIED_EMAIL": True
        },
        "google": {
            # For each OAuth based provider, either add a ``SocialApp``
            # (``socialaccount`` app) containing the required client
            # credentials, or list them here:
            "APP": {
                "client_id": "123",
                "secret": "456",
                "key": ""
            },
            # These are provider-specific settings that can only be
            # listed here:
            "SCOPE": [
                "profile",
                "email",
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
            }
        }
    }

``SOCIALACCOUNT_QUERY_EMAIL`` (default: ``ACCOUNT_EMAIL_REQUIRED``)
  Request email address from 3rd party account provider? E.g. using
  OpenID AX, or the Facebook "email" permission.

``SOCIALACCOUNT_SOCIALACCOUNT_STR`` (default: ``str`` of user object)
  Used to override the str value for the SocialAccount model.

  Must be a function accepting a single parameter for the socialaccount object.

``SOCIALACCOUNT_STORE_TOKENS`` (default: ``False``)
  Indicates whether or not the access tokens are stored in the database.
