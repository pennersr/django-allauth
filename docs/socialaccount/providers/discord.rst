Discord
-------

App registration and management (get your key and secret here)
    https://discordapp.com/developers/applications/me

Make sure to Add Redirect URI to your application.

Development callback (redirect) URL
    http://127.0.0.1:8000/accounts/discord/login/callback/

It's required to request the `identify` scope to fetch the user ID.
