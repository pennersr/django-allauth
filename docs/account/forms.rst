Forms
=====

Login
*****

*Path*:
  ``allauth.account.forms.LoginForm``
*Used on*:
  `account_login <views.html#login-account-login>`__ view.

Example override::

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

Signup
******

*Path*:
  ``allauth.account.forms.SignupForm``
*Used on*:
  `account_signup <views.html#signup-account-signup>`__ view.

Example override::

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


Add Email
*********

*Path*:
  ``allauth.account.forms.AddEmailForm``
*Used on*:
   `account_email <views.html#emails-management-account-email>`__ view.

Example override::

    from allauth.account.forms import AddEmailForm
    class MyCustomAddEmailForm(AddEmailForm):

        def save(self, request):

            # Ensure you call the parent class's save.
            # .save() returns an allauth.account.models.EmailAddress object.
            email_address_obj = super(MyCustomAddEmailForm, self).save(request)

            # Add your own processing here.

            # You must return the original result.
            return email_address_obj

You have access to the following:

- ``self.user`` is the User object that is logged in.

``settings.py``::

    ACCOUNT_FORMS = {'add_email': 'mysite.forms.MyCustomAddEmailForm'}


Change Password
***************

*Path*:
  ``allauth.account.forms.ChangePasswordForm``
*Used on*:
  `account_change_password <views.html#password-management>`__ view.

Example override::

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


Set Password
************

*Path*:
  ``allauth.account.forms.SetPasswordForm``
*Used on*:
  `account_set_password <views.html#password-management>`__ view.

Example override::

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

Reset Password
**************

*Path*:
  ``allauth.account.forms.ResetPasswordForm``
*Used on*:
  `account_reset_password <views.html#password-reset-account-reset-password>`__ view.

Example override::

    from allauth.account.forms import ResetPasswordForm
    class MyCustomResetPasswordForm(ResetPasswordForm):

        def save(self, request):

            # Ensure you call the parent class's save.
            # .save() returns a string containing the email address supplied
            email_address = super(MyCustomResetPasswordForm, self).save(request)

            # Add your own processing here.

            # Ensure you return the original result
            return email_address

You have access to the following:

- ``self.users`` is a list of all possible User objects with matching email address.

``settings.py``::

    ACCOUNT_FORMS = {'reset_password': 'mysite.forms.MyCustomResetPasswordForm'}


Reset Password From Key
***********************

*Path*:
  ``allauth.account.forms.ResetPasswordKeyForm``
*Used on*:
  `account_reset_password <views.html#password-reset-account-reset-password>`__ view.

Example override::

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
