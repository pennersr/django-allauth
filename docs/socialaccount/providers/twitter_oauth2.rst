X/Twitter (OAuth 2)
-------------------

You will need to create an X app with OAuth 2.0 enabled and configure the X provider for
your Django application via the admin interface.

App registration
****************

To register an app on X you will need an X account. With an account, you can
create a new app via::

    https://developer.x.com/en/portal/dashboard

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000/accounts/twitter_oauth2/login/callback/

For production use a callback URL such as::

   http://{{yourdomain}}.com/accounts/twitter_oauth2/login/callback/


App database configuration through admin
****************************************

The second part of setting up the X provider requires you to configure
your Django application. Configuration is done by creating a SocialApp object
in the admin. Add a social app on the admin page::

    /admin/socialaccount/socialapp/

Use the X keys tab of your application to fill in the form. It's located::

    https://developer.x.com/en/portal/projects/{project-id}/apps/{app-id}/keys

The configuration is as follows:

* Provider ID: "twitter_oauth2"
* Name, your pick, suggest "X"
* Client id, is called "OAuth2.0 Client ID" on X
* Secret key, is called "OAuth2.0 Client Secret" on X
* Key, is not needed, leave blank
