Tumblr OAuth2
--------------

You will need to create a Tumblr app and configure the Tumblr provider for
your Django application via the admin interface.

App registration
****************

To register an app on Tumblr you will need a Tumblr account. With an account, you
can create a new app via::

    https://www.tumblr.com/oauth/register

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000/accounts/tumblr_oauth2/login/callback/

For production use a callback URL such as::

   https://{{yourdomain}}.com/accounts/tumblr_oauth2/login/callback/


App database configuration through admin
****************************************

The second part of setting up the Tumblr provider requires you to configure
your Django application. Configuration is done by creating a SocialApp object
in the admin. Add a social app on the admin page::

    /admin/socialaccount/socialapp/

Use the tumblr keys tab of your application to fill in the form. It's located::

    https://www.tumblr.com/oauth/apps

The configuration is as follows:

* Provider, "Tumblr"
* Name, your pick, suggest "Tumblr"
* Client id, is called "OAuth2.0 Client ID" on Tumblr
* Secret key, is called "OAuth2.0 Client Secret" on Tumblr
* Key, is not needed, leave blank


You can also set up the provider in `settings.py`::

    SOCIALACCOUNT_PROVIDERS = {
        "tumblr": {
            "SCOPE": ["basic", "write"],
            "APP": {
                "client_id": os.environ.get("TUMBLR_CLIENT_ID", ""),
                "secret": os.environ.get("TUMBLR_CLIENT_SECRET", ""),
                "key": "",
            },
        },
    }

For more information about the Tumblr API, see::

    https://www.tumblr.com/docs/en/api/v2