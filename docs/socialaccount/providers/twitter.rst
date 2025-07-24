X/Twitter (OAuth 1)
-------------------

You will need to create an X app and configure the X provider for your Django
application via the admin interface.

App registration
****************

To register an app on X you will need an X account. With an account, you can
create a new app via::

    https://developer.x.com/en/portal/apps/new

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000/accounts/twitter/login/callback/

X won't allow using http://localhost:8000.

For production use a callback URL such as::

   http://{{yourdomain}}.com/accounts/twitter/login/callback/

To allow users to login without authorizing each session, select "Allow this
application to be used to Sign in with X" under the application's
"Settings" tab.

App database configuration through admin
****************************************

The second part of setting up the X provider requires you to configure
your Django application. Configuration is done by creating a Socialapp object
in the admin. Add a social app on the admin page::

    /admin/socialaccount/socialapp/

Use the X keys tab of your application to fill in the form. It's located::

    https://developer.x.com/en/portal/apps/{{yourappid}}/keys

The configuration is as follows:

* Provider ID: "twitter"
* Name, your pick, suggest "X"
* Client id, is called "Consumer Key (API Key)" on X
* Secret key, is called "Consumer Secret (API Secret)" on X
* Key, is not needed, leave blank
