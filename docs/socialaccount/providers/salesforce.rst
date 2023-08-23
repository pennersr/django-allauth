Salesforce
----------

The Salesforce provider requires you to set the login VIP as the provider
model's 'key' (in addition to client id and secret). Production environments
use https://login.salesforce.com/. Sandboxes use https://test.salesforce.com/.

HTTPS is required for the callback.

Development callback URL
    https://localhost:8000/accounts/salesforce/login/callback/

Salesforce OAuth2 documentation
    https://developer.salesforce.com/page/Digging_Deeper_into_OAuth_2.0_on_Force.com

To Use:

- Include allauth.socialaccount.providers.salesforce in INSTALLED_APPS
- In a new Salesforce Developer Org, create a Connected App
  with OAuth (minimum scope id, openid), and a callback URL
- Create a Social application in Django admin, with client id,
  client key, and login_url (in "key" field)
