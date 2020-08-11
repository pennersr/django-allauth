Forms
=====

The following forms can be overridden as needed in order to:

- Add extra fields for extra required information
- Override save to add extra functionality on save

Overriding Save
---------------

If you decide to add fields to a form, you will need to
manually save the custom fields' data.

ACCOUNT_FORMS
-------------

Default Settings::

    ACCOUNT_FORMS = {
        'login': 'allauth.account.forms.LoginForm',
        'signup': 'allauth.account.forms.SignupForm',
        'add_email': 'allauth.account.forms.AddEmailForm',
        'change_password': 'allauth.account.forms.ChangePasswordForm',
        'set_password': 'allauth.account.forms.SetPasswordForm',
        'reset_password': 'allauth.account.forms.ResetPasswordForm',
        'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
        'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    }

login (``allauth.account.forms.LoginForm``)
*******************************************

Used on `account_login <views.html#login-account-login>`__ view.

``save`` is not called, you need to override ``login``
::

    from allauth.account.forms import LoginForm
    class MyCustomLoginForm(LoginForm):

        def login(self, *args, **kwargs):

            # Add your own processing here.

            # You must return the original result.
            return super(MyCustomLoginForm, self).login(*args, **kwargs)

You have access to the following:

- ``self.user`` is the User object that is logging in.

``settings.py``::

    ACCOUNT_FORMS = {'login': 'mysite.forms.MyCustomLoginForm'}

signup (``allauth.account.forms.SignupForm``)
*********************************************

Used on `account_signup <views.html#signup-account-signup>`__ view.

::

    from allauth.account.forms import SignupForm
    class MyCustomSignupForm(SignupForm):

        def save(self, request):

            # Ensure you call the parent class's save.
            # .save() returns a User object.
            user = super(MyCustomSignupForm, self).save(request)

            # Add your own processing here.

            # You must return the original result.
            return user

``settings.py``::

    ACCOUNT_FORMS = {'signup': 'mysite.forms.MyCustomSignupForm'}

add_email (``allauth.account.forms.AddEmailForm``)
**************************************************

Used on `account_email <views.html#e-mails-management-account-email>`__ view.

::

    from allauth.account.forms import AddEmailForm
    class MyCustomAddEmailForm(AddEmailForm):

        def save(self):

            # Ensure you call the parent class's save.
            # .save() returns an allauth.account.models.EmailAddress object.
            email_address_obj = super(MyCustomAddEmailForm, self).save()

            # Add your own processing here.

            # You must return the original result.
            return email_address_obj

You have access to the following:

- ``self.user`` is the User object that is logged in.

``settings.py``::

    ACCOUNT_FORMS = {'add_email': 'mysite.forms.MyCustomAddEmailForm'}

change_password (``allauth.account.forms.ChangePasswordForm``)
**************************************************************

Used on `account_change_password <views.html#password-management>`__ view.

::

    from allauth.account.forms import ChangePasswordForm
    class MyCustomChangePasswordForm(ChangePasswordForm):

        def save(self):

            # Ensure you call the parent class's save.
            # .save() does not return anything
            super(MyCustomChangePasswordForm, self).save()

            # Add your own processing here.

You have access to the following:

- ``self.user`` is the User object that is logged in.

``settings.py``::

    ACCOUNT_FORMS = {'change_password': 'mysite.forms.MyCustomChangePasswordForm'}

set_password (``allauth.account.forms.SetPasswordForm``)
********************************************************

Used on `account_set_password <views.html#password-management>`__ view.

::

    from allauth.account.forms import SetPasswordForm
    class MyCustomSetPasswordForm(SetPasswordForm):

        def save(self):

            # Ensure you call the parent class's save.
            # .save() does not return anything
            super(MyCustomSetPasswordForm, self).save()

            # Add your own processing here.

You have access to the following:

- ``self.user`` is the User object that is logged in.

``settings.py``::

    ACCOUNT_FORMS = {'set_password': 'mysite.forms.MyCustomSetPasswordForm'}

reset_password (``allauth.account.forms.ResetPasswordForm``)
************************************************************

Used on `account_reset_password <views.html#password-reset-account-reset-password>`__ view.

::

    from allauth.account.forms import ResetPasswordForm
    class MyCustomResetPasswordForm(ResetPasswordForm):

        def save(self):

            # Ensure you call the parent class's save.
            # .save() returns a string containing the email address supplied
            email_address = super(MyCustomResetPasswordForm, self).save()

            # Add your own processing here.

            # Ensure you return the original result
            return email_address

You have access to the following:

- ``self.users`` is a list of all possible User objects with matching email address.

``settings.py``::

    ACCOUNT_FORMS = {'reset_password': 'mysite.forms.MyCustomResetPasswordForm'}

reset_password_from_key (``allauth.account.forms.ResetPasswordKeyForm``)
************************************************************************

Used on `account_reset_password <views.html#password-reset-account-reset-password>`__ view.

::

    from allauth.account.forms import ResetPasswordKeyForm
    class MyCustomResetPasswordKeyForm(ResetPasswordKeyForm):

        def save(self):

            # Add your own processing here.

            # Ensure you call the parent class's save.
            # .save() does not return anything
            super(MyCustomResetPasswordKeyForm, self).save()

You have access to the following:

- ``self.user`` is the User object.

``settings.py``::

    ACCOUNT_FORMS = {'reset_password_from_key': 'mysite.forms.MyCustomResetPasswordKeyForm'}

SOCIALACCOUNT_FORMS
-------------------

Default Settings::

    SOCIALACCOUNT_FORMS = {
        'login': 'allauth.socialaccount.forms.DisconnectForm',
        'signup': 'allauth.socialaccount.forms.SignupForm',
    }

signup (``allauth.socialaccount.forms.SignupForm``)
***************************************************

Used on socialaccount_signup view used when someone initially signs up
with a social account and needs to create an account.

::

    from allauth.socialaccount.forms import SignupForm
    class MyCustomSocialSignupForm(SignupForm):

        def save(self):

            # Ensure you call the parent class's save.
            # .save() returns a User object.
            user = super(MyCustomSocialSignupForm, self).save()

            # Add your own processing here.

            # You must return the original result.
            return user

You have access to the following:

- ``self.socialaccount``

``settings.py``::

    SOCIALACCOUNT_FORMS = {'signup': 'mysite.forms.MyCustomSocialSignupForm'}

disconnect (``allauth.socialaccount.forms.DisconnectForm``)
***********************************************************

Used on socialaccount_connections view, used when removing a social account.

::

    from allauth.socialaccount.forms import DisconnectForm
    class MyCustomSocialDisconnectForm(DisconnectForm):

        def save(self):

            # Add your own processing here if you do need access to the
            # socialaccount being deleted.

            # Ensure you call the parent class's save.
            # .save() does not return anything
            super(MyCustomSocialDisconnectForm, self).save()

            # Add your own processing here if you don't need access to the
            # socialaccount being deleted.

You have access to the following:

- ``self.request`` is the request object
- ``self.accounts`` is a list containing all of the user's SocialAccount objects.
- ``self.cleaned_data['account']`` contains the socialaccount being deleted. ``.save()``
  issues the delete. So if you need access to the socialaccount beforehand, move your
  code before ``.save()``.

``settings.py``::

    SOCIALACCOUNT_FORMS = {'disconnect': 'mysite.forms.MyCustomSocialDisconnectForm'}
