Twitter
-------

You will need to create a Twitter app and configure the Twitter provider for
your Django application via the admin interface.

App registration
****************

To register an app on Twitter you will need a Twitter account. With an account, you
can create a new app via::

    https://apps.twitter.com/app/new

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000/accounts/twitter/login/callback/

Twitter won't allow using http://localhost:8000.

For production use a callback URL such as::

   http://{{yourdomain}}.com/accounts/twitter/login/callback/

To allow users to login without authorizing each session, select "Allow this
application to be used to Sign in with Twitter" under the application's
"Settings" tab.

App database configuration through admin
****************************************

The second part of setting up the Twitter provider requires you to configure
your Django application. Configuration is done by creating a Socialapp object
in the admin. Add a social app on the admin page::

    /admin/socialaccount/socialapp/

Use the twitter keys tab of your application to fill in the form. It's located::

    https://apps.twitter.com/app/{{yourappid}}/keys

The configuration is as follows:

* Provider, "Twitter"
* Name, your pick, suggest "Twitter"
* Client id, is called "Consumer Key (API Key)" on Twitter
* Secret key, is called "Consumer Secret (API Secret)" on Twitter
* Key, is not needed, leave blank
