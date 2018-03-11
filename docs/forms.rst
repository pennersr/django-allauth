Forms
=====

The following forms can be overridden as needed.

- Add extra fields for extra required information
- Override save to add extra functionality on save

Overriding Save
---------------

If you decide to add fields to a form, you will need to
manually save the custom fields data.

::

    from allauth.account.forms import SignupForm
    class MyCustomSignupForm(SignupForm):

        def save(self):

            # Ensure you call the parent classes save before your own processing
            super(MyCustomSignupForm, self).save()



ACCOUNT_FORMS
=============

Default Settings::

    ACCOUNT_FORMS = {
        'login': 'allauth.account.forms.LoginForm',
        'signup': 'allauth.account.forms.SignupForm',
        'add_email': 'allauth.account.forms.AddEmailForm',
        'change_password': 'allauth.account.forms.ChangePasswordForm',
        'set_password': 'allauth.account.forms.SetPasswordForm',
        'reset_password': 'allauth.account.forms.ResetPasswordForm',
        'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    }

login (``allauth.account.forms.LoginForm``)
-------------------------------------------

signup (``allauth.account.forms.SignupForm``)
---------------------------------------------

add_email (``allauth.account.forms.AddEmailForm``)
--------------------------------------------------

change_password (``allauth.account.forms.ChangePasswordForm``)
--------------------------------------------------------------

set_password (``allauth.account.forms.SetPasswordForm``)
--------------------------------------------------------

reset_password (``allauth.account.forms.ResetPasswordForm``)
------------------------------------------------------------

reset_password_from_key (``allauth.account.forms.ResetPasswordKeyForm``)
------------------------------------------------------------------------


SOCIALACCOUNT_FORMS
===================

Default Settings::

    SOCIALACCOUNT_FORMS = {
        'login': 'allauth.socialaccount.forms.DisconnectForm',
        'signup': 'allauth.socialaccount.forms.SignupForm',
    }

signup (``allauth.socialaccount.forms.SignupForm``)
---------------------------------------------------

disconnect (``allauth.socialaccount.forms.DisconnectForm``)
-----------------------------------------------------------

