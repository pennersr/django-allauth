Notion
------

After creating an integration perform the following steps:

1. Navigate to your integration then Capabilities, User Capabilities, and select 'Read user information including email addresses.' 
2. Click 'Distribution' and check 'yes' on 'Do you want to make this integration public?'.
3. In the 'Redirect URL' paste the callback URL below. Notion only allows using 'http' for 'localhost' - do not use 127.0.0.1.

App registration (get your key and secret here)
    https://www.notion.so/my-integrations

Development callback URL
    http://localhost:8000/accounts/notion/login/callback/
