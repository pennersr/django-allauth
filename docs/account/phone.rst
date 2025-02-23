Phone
=====

Installation
************

FIXME


Form Fields
***********

For presenting a phone number form field to the user a basic ``<input type="tel">`` field
is used that requires input in E164 format. There are various external projects that offer more
elaborate phone number input fields. You can switch over to using the fields provided by those projects
by overriding the following adapter method:

.. autoclass:: allauth.account.adapter.DefaultAccountAdapter

   .. automethod:: phone_form_field


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

For sending SMS messages, various eternal providers and packages are
available. You can integrate those by overriding the following adapter method:

 .. autoclass:: allauth.account.adapter.DefaultAccountAdapter

   .. automethod:: send_phone_verification_code
