Feishu
------

App Registration
  https://open.feishu.cn/app

Authorized Redirect URI
    http://127.0.0.1:8000/accounts/feishu/login/callback/

Into the developer background https://open.feishu.cn/app, click on the create self-built application, obtain app_id and app_secret.
In the configuration of application security domain name added to redirect URL, such as https://open.feishu.cn/document.
Redirect URL is the interface through which the application obtains the user's identity by using the user login pre-authorization code after the user has logged in.
If it is not configured or configured incorrectly, the open platform will prompt the request to be illegal.
