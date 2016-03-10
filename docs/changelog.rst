Changelog
---------

This chapter contains notes on upgrading.

From 0.24.1
***********

- In order to be secure by default, users are now blocked from logging
  in after exceeding a maximum number of failed login attempts
  (see `ACCOUNT_LOGIN_ATTEMPTS_LIMIT`, `ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT`). Set
  `ACCOUNT_LOGIN_ATTEMPTS_LIMIT` to `None` to disable this functionality.

- The signature of the adapter method `format_email_subject` has
  changed.  It now takes the email template `context` as a second
  parameter.

From 0.24.0
***********

- Setting a password after logging in with a social account no longer logs out
  the user by default on Django 1.7+. Setting an initial password and changing
  the password both respect `settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`.

From 0.23.0
***********

- Increased `SocialApp` key/secret/token sizes to 191, decreased
  `SocialAccount.uid` size to 191. The latter was done in order to
  accomodate for MySQL in combination with utf8mb4 and contraints on
  `uid`. Note that `uid` is used to store OpenID URLs, which can
  theoretically be longer than 191 characters, although in practice
  this does not seem to be the case. In case you really need to
  control the `uid` length, set `settings.SOCIALACCOUNT_UID_MAX_LENGTH`
  accordingly. Migrations are in place.

From 0.21.0
***********

- Dropped support for Python 2.6 and Django <1.6.

- The default Facebook Graph API version is now v2.4.

- Template context processors are no longer used. The context
  processor for ``allauth.account`` was already empty, and the context
  processor for ``allauth.socialaccount`` has been converted into the
  :doc:`{% get_providers %} <templates>` template tag.


From 0.20.0
***********

- In version 0.20.0 an `account` migration (`0002_email_max_length`)
  was added to alter the maximum length of the email
  field. Unfortunately, a side effect of this migration was that the
  `unique=True` setting slipped through as well. Hardcoding this to
  `True` is wrong, as uniqueness actually depends on the
  `ACCOUNT_UNIQUE_EMAIL` setting. We cannot create a followup `0003`
  migration to set things straight, as the `0002` migration may fail
  on installations where email addresses are not unique. Therefore, we
  had to resort to changing an existing migration which is normally
  not the right thing to do. In case your installation has
  `ACCOUNT_UNIQUE_EMAIL` set to `True`, you need not take any further
  action. In case it is set to `False` and migration `0002` already
  ran, please issue a `--fake` migration down to `0001`, followed by a
  re-run of the updated `0002`.

From 0.19.1
***********

- Given that the `max_length` for the Django 1.8 `EmailField` has been
  bumped to 254, allauth is following up. Migrations (`account`) are
  in place.

From 0.18.0
***********

- In the upcoming Django 1.8 it is no longer possible to hookup an
  unsaved `User` instance to a `SocialAccount`. Therefore, if you are
  inspecting the `sociallogin` object, you should now use
  `sociallogin.user` instead of `sociallogin.account.user`.

- When users logged in while `User.is_active` was `False`, they were
  sent to `/accounts/inactive/` in case of a social login, and
  received a form validation error in case of a local login. This
  needless inconsistency has been removed. The validation error no
  longer appears and local logins are also redirected to
  `/accounts/inactive/`.

- In case you were overriding the `ResetPasswordForm`: the save method
  now takes `request` as its first argument.

- All existing migrations have been moved into `south_migrations`
  packages, this in order not to conflict with Django's built-in
  support for migrations. South 1.0 automatically picks up this new
  location. Upgrade South if you are still dependent on these
  migrations.

From 0.17.0
***********

- The Persona provider now requires the `AUDIENCE` parameter to be
  explicitly configured, as required by the Persona specification for
  security reasons.

- The inline Javascript is removed from the `fbconnect.html` template,
  which allows for a more strict `Content-Security-Policy`. If you
  were using the builtin `fbconnect.html` this change should go by
  unnoticed.

From 0.15.0
***********

- Previously, the `save(user)` was called on the custom signup form.
  However, this shadowed the existing `save` method in case a model
  form was used. To avoid confusion, the `save` method has been
  deprecated in favour of a `def signup(request, user)` method.

- The Amazon provider requires more space for `token_secret`, so the
  maximum length restriction has been dropped. Migrations are in
  place.


From 0.14.2
***********

- The `/accounts/login/` view now supports AJAX requests.

- Instead of directly rendering and returning a template, logging in
  while the account is inactive or not yet confirmed now redirects to
  two new views: `/accounts/inactive/` respectively
  `/accounts/confirm-email/`.

- The `account/verification_sent.html` template no longer receives the
  e-mail address in the context (`email`). Note that a message
  containing that e-mail address is still emitted using the messages
  framework.

- The `/accounts/confirm_email/key/` view has been
  renamed to `/accounts/confirm-email/` (human friendlier). Redirects
  are in place to handle old still pending confirmations.

- Built-in support for django-avatar has been removed. Offering such
  functionality means making choices which may not be valid for
  everyone. For example, allauth was downloading the image (which can
  take some time, or even block) in the context of the login, whereas
  a better place might be some celery background job. Additionally, in
  case of an error it simply ignored this. How about retries et al?
  Also, do you want to copy the avatar once at sign up, or do you want
  to update on each login? All in all, this functionality goes way
  beyond authentication and should be addressed elsewhere, beyond
  allauth scope. The original code has been preserved here so that you
  can easily reinstate it in your own project:
  https://gist.github.com/pennersr/7571752


From 0.14.1
***********

- In case you were using the internal method
  `generate_unique_username`, note that its signature has changed. It
  now takes a list of candidates to base the username on.

From 0.13.0
***********

- The `socialaccount/account_inactive.html` template has been
  moved to `account/account_inactive.html`.

- The adapter API for creating and populating users has been
  overhauled. As a result, the `populate_new_user` adapter methods
  have disappeared. Please refer to the section on "Creating and
  Populating User Instances" for more information.

From 0.12.0
***********

- All account views are now class-based.

- The password reset from key success response now redirects to a
  "done" view (`/accounts/password/reset/key/done/`). This view has
  its own `account/password_reset_from_key_done.html` template. In
  previous versions, the success template was intertwined with the
  `account/password_reset_from_key.html` template.

From 0.11.1
***********

- The `{% provider_login_url %}` tag now takes an optional process
  parameter that indicates how to process the social login. As a
  result, if you include the template
  `socialaccount/snippets/provider_list.html` from your own overriden
  `socialaccount/connections.html` template, you now need to pass
  along the process parameter as follows:
  `{% include "socialaccount/snippets/provider_list.html" with process="connect" %}`.

- Instead of inlining the required Facebook SDK Javascript wrapper
  code into the HTML, it now resides into its own .js file (served
  with `{% static %}`). If you were using the builtin `fbconnect.html`
  this change should go by unnoticed.

From 0.9.0
**********

- Logout no longer happens on GET request. Refer to the `LogoutView`
  documentation for more background information. Logging out on GET
  can be restored by the setting `ACCOUNT_LOGOUT_ON_GET`. Furthermore,
  after logging out you are now redirected to
  `ACCOUNT_LOGOUT_REDIRECT_URL` instead of rendering the
  `account/logout.html` template.

- `LOGIN_REDIRECT_URLNAME` is now deprecated. Django 1.5 accepts both
  URL names and URLs for `LOGIN_REDIRECT_URL`, so we do so as well.

- `DefaultAccountAdapter.stash_email_verified` is now named
  `stash_verified_email`.

- Django 1.4.3 is now the minimal requirement.

- Dropped dependency on (unmaintained?) oauth2 package, in favor of
  requests-oauthlib. So you will need to update your (virtual)
  environment accordingly.

- We noticed a very rare bug that affects end users who add Google
  social login to existing accounts. The symptom is you end up with
  users who have multiple primary email addresses which conflicts
  with assumptions made by the code. In addition to fixing the code
  that allowed duplicates to occur, there is a managegement command
  you can run if you think this effects you (and if it doesn't effect
  you there is no harm in running it anyways if you are unsure):

  - `python manage.py account_unsetmultipleprimaryemails`

    - Will silently remove primary flags for email addresses that
      aren't the same as `user.email`.

    - If no primary `EmailAddress` is `user.email` it will pick one
      at random and print a warning.

- The expiry time, if any, is now stored in a new column
  `SocialToken.expires_at`. Migrations are in place.

- Furthermore, Facebook started returning longer tokens, so the
  maximum token length was increased. Again, migrations are in place.

- Login and signup views have been turned into class-based views.

- The template variable `facebook_perms` is no longer passed to the
  "facebook/fbconnect.html" template. Instead, `fb_login_options`
  containing all options is passed.

From 0.8.3
**********

- `requests` is now a dependency (dropped `httplib2`).

- Added a new column `SocialApp.client_id`. The value of `key` needs
  to be moved to the new `client_id` column. The `key` column is
  required for Stack Exchange. Migrations are in place to handle all
  of this automatically.

From 0.8.2
**********

- The `ACCOUNT_EMAIL_VERIFICATION` setting is no longer a boolean
  based setting. Use a string value of "none", "optional" or
  "mandatory" instead.

- The template "account/password_reset_key_message.txt" has been moved
  to "account/email/password_reset_key_message.txt". The subject of
  the message has been moved into a template
  ("account/email/password_reset_key_subject.txt").

- The `site` foreign key from `SocialApp` to `Site` has been replaced
  by a `ManyToManyField`. Many apps can be used across multiple
  domains (Facebook cannot).


From 0.8.1
**********

- Dropped support for `CONTACT_EMAIL` from the `account` template
  context processor. It was never documented and only used in the
  templates as an example -- there is no need to pollute the `allauth`
  settings with that. If your templates rely on it then you will have
  to put it in a context processor yourself.

From 0.7.0
**********

- `allauth` now depends on Django 1.4 or higher.

- Major impact: dropped dependency on the `emailconfirmation` app, as
  this project is clearly left unmaintained. Important tickets such
  as https://github.com/pinax/django-email-confirmation/pull/5 are not
  being addressed. All models and related functionality have been
  directly integrated into the `allauth.account` app. When upgrading
  take care of the following:

  - The `emailconfirmation` setting `EMAIL_CONFIRMATION_DAYS` has been
    replaced by `ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS`.

  - Instead of directly confirming the e-mail address upon the GET
    request the confirmation is now processed as part of an explicit
    POST. Therefore, a new template `account/email_confirm.html` must
    be setup.

  - Existing `emailconfirmation` data should be migrated to the new
    tables. For this purpose a special management command is
    available: `python manage.py
    account_emailconfirmationmigration`. This command does not drop
    the old `emailconfirmation` tables -- you will have to do this
    manually yourself. Why not use South? EmailAddress uniqueness
    depends on the configuration (`ACCOUNT_UNIQUE_EMAIL`), South does
    not handle settings dependent database models.

- `{% load account_tags %}` is deprecated, simply use: `{% load account %}`

- `{% load socialaccount_tags %}` is deprecated, simply use:
  `{% load socialaccount %}`

From 0.5.0
**********

- The `ACCOUNT_EMAIL_AUTHENTICATION` setting has been dropped in favor
  of `ACCOUNT_AUTHENTICATION_METHOD`.

- The login form field is now always named `login`. This used to by
  either `username` or `email`, depending on the authentication
  method. If needed, update your templates accordingly.

- The `allauth` template tags (containing template tags for
  OpenID, Twitter and Facebook) have been removed. Use the
  `socialaccount` template tags instead (specifically: `{% provider_login_url
  ... %}`).

- The `allauth.context_processors.allauth` context processor has been
  removed, in favor of
  `allauth.socialaccount.context_processors.socialaccount`. In doing
  so, all hardcodedness with respect to providers (e.g
  `allauth.facebook_enabled`) has been removed.


From 0.4.0
**********

- Upgrade your `settings.INSTALLED_APPS`: Replace `allauth.<provider>`
  (where provider is one of `twitter`, `facebook` or `openid`) with
  `allauth.socialaccount.providers.<provider>`

- All provider related models (`FacebookAccount`, `FacebookApp`,
  `TwitterAccount`, `TwitterApp`, `OpenIDAccount`) have been unified
  into generic `SocialApp` and `SocialAccount` models. South migrations
  are in place to move the data over to the new models, after which
  the original tables are dropped. Therefore, be sure to run migrate
  using South.
