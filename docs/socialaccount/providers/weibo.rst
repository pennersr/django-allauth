Weibo
-----

Register your OAuth2 app over at ``http://open.weibo.com/apps``. Unfortunately,
Weibo does not allow for specifying a port number in the authorization
callback URL. So for development purposes you have to use a callback url of
the form ``http://127.0.0.1/accounts/weibo/login/callback/`` and run
``runserver 127.0.0.1:80``.
