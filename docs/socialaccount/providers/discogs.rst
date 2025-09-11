Discogs (OAuth 1a)
------------------

You will need to register a Discogs app to obain a consumer key and secret.

App registration
****************

To register an app you will need a Discogs account.

With an account, you can create a new app at::

    https://www.discogs.com/settings/developers

In the app creation form (optionally) fill in the development callback URL::

    http://127.0.0.1:8000/accounts/discogs/login/callback/

For production use a callback URL such as::

   https://{{yourdomain}}.com/accounts/discogs/login/callback/


Setting up provider
*******************

* 'name', up to you to choose (optional)
* 'client_id', is called "Consumer Key"
* 'secret', is called "Consumer Secret"
