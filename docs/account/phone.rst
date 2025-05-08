Phone
=====

Installation
************

In addition to following the overall instructions, pay attention to the
following in the ``settings.py`` of your project::

  # Make sure that the login methods includes "phone" as a method.
  ACCOUNT_LOGIN_METHODS = {"phone", "email"}

  # Add a required phone field to the signup fields.
  # ACCOUNT_SIGNUP_FIELDS = [
    'phone*',
    'email*'  # Can be left out if you want to only use 'phone'.
  ]

  # You will need to provide methods for storing phone numbers, and
  # sending SMS messages in a custom adapter.
  ACCOUNT_ADAPTER = 'project.users.adapter.MyAccountAdapter'


Configuration
=============

Available settings:

``ACCOUNT_PHONE_VERIFICATION_ENABLED`` (default: ``True``)
  Whether or not mandatory verification of phone numbers during login/signup takes place.

``ACCOUNT_PHONE_VERIFICATION_MAX_ATTEMPTS`` (default: ``3``)
  This setting controls the maximum number of attempts the user has at inputting
  a valid code.

``ACCOUNT_PHONE_VERIFICATION_TIMEOUT`` (default: ``900``)
  The code that is sent has a limited life span. It expires this many seconds after
  which it was sent.

``ACCOUNT_PHONE_VERIFICATION_SUPPORTS_CHANGE`` (default: ``False``)
  Whether or not the phone number can be changed after signup at the
  phone number verification stage.

  **Warning**: the warning related to enumeration prevent over at
   ``ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE`` holds here as well.

``ACCOUNT_PHONE_VERIFICATION_SUPPORTS_RESEND`` (default: ``False``)
  Whether or not the user can request a new phone number verification code.


Form Fields
***********

For presenting a phone number form field to the user a basic ``<input type="tel">`` field
is used that requires input in E164 format. There are various external projects
that offer more elaborate phone number input fields. You can switch over to
using the fields provided by those projects, or, tweak the phone number
validaton logic, by overriding the following adapter methods:

.. autoclass:: allauth.account.adapter.DefaultAccountAdapter

   .. automethod:: phone_form_field
   .. automethod:: clean_phone


Database Models
***************

Out of the box, there are no models provided intended to store the phone numbers
of users.  It is up to the developer to decide where phone numbers are to be
stored, for example, on a custom user model, or, on a separate `Phone` model of
its own. Once those the models are setup, the following adapter methods need to
be populated so that the models will be used:

 .. autoclass:: allauth.account.adapter.DefaultAccountAdapter

   .. automethod:: get_phone
   .. automethod:: set_phone
   .. automethod:: set_phone_verified
   .. automethod:: get_user_by_phone


Sending SMS Messages
********************

For sending SMS messages, various external providers and packages are
available. You can integrate those by overriding the following adapter method:

 .. autoclass:: allauth.account.adapter.DefaultAccountAdapter

   .. automethod:: send_verification_code_sms
   .. automethod:: send_unknown_account_sms
