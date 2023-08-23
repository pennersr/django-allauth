Stripe
------

You register your OAUth2 app via the Connect->Settings page of the Stripe
dashboard:

 https://dashboard.stripe.com/account/applications/settings

This page will provide you with both a Development and Production `client_id`.

You can also register your OAuth2 app callback on the Settings page in the
"Website URL" box, e.g.:

 http://example.com/accounts/stripe/login/callback/

However, the OAuth2 secret key is not on this page. The secret key is the same
secret key that you use with the Stripe API generally. This can be found on the
Stripe dashboard API page:

 https://dashboard.stripe.com/account/apikeys

See more in documentation
 https://stripe.com/docs/connect/standalone-accounts
