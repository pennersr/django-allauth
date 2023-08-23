Amazon Cognito
--------------

App registration (get your key and secret here)
  1. Go to your https://console.aws.amazon.com/cognito/ and create a Cognito User Pool if you haven't already.
  2. Go to General Settings > App Clients section and create a new App Client if you haven't already. Please make sure you select the option to generate a secret key.
  3. Go to App Integration > App Client Settings section and:

    1. Enable Cognito User Pool as an identity provider.
    2. Set the callback and sign-out URLs. (see next section for development callback URL)
    3. Enable Authorization Code Grant OAuth flow.
    4. Select the OAuth scopes you'd like to allow.

  4. Go to App Integration > Domain Name section and create a domain prefix for your Cognito User Pool.

Development callback URL:
  http://localhost:8000/accounts/amazon-cognito/login/callback/

In addition, you'll need to specify your user pool's domain like so:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'amazon_cognito': {
            'DOMAIN': 'https://<domain-prefix>.auth.us-east-1.amazoncognito.com',
        }
    }

Your domain prefix is the value you specified in step 4 of the app registration process.
If you provided a custom domain such as accounts.example.com provide that instead.
