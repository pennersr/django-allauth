Forms
=====

Signup
******

*Path*:
  ``allauth.socialaccount.forms.SignupForm``

*Used on*:
  ``socialaccount_signup`` view used when a user initially signs up
  with a social account and needs to create an account.

Example override::

    from allauth.socialaccount.forms import SignupForm
    class MyCustomSocialSignupForm(SignupForm):

        def save(self, request):

            # Ensure you call the parent class's save.
            # .save() returns a User object.
            user = super(MyCustomSocialSignupForm, self).save(request)

            # Add your own processing here.

            # You must return the original result.
            return user

You have access to the following:

- ``self.socialaccount``

``settings.py``::

    SOCIALACCOUNT_FORMS = {'signup': 'mysite.forms.MyCustomSocialSignupForm'}

Disconnect
**********

*Path*:
  ``allauth.socialaccount.forms.DisconnectForm``
*Used on*:
  ``socialaccount_connections`` view, used when removing a social account.

Example override::

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
