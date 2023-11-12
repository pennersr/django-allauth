Sending Email
=============

Emails sent (e.g. in case of password forgotten or email
confirmation) can be altered by providing your own
templates. Templates are named as follows::

    account/email/email_confirmation_signup_subject.txt
    account/email/email_confirmation_signup_message.txt

    account/email/email_confirmation_subject.txt
    account/email/email_confirmation_message.txt

In case you want to include an HTML representation, add an HTML
template as follows::

    account/email/email_confirmation_signup_message.html

    account/email/email_confirmation_message.html

The project does not contain any HTML email templates out of the box.
When you do provide these yourself, note that both the text and HTML
versions of the message are sent.

If this does not suit your needs, you can hook up your own custom
mechanism by overriding the ``send_mail`` method of the account adapter
(``allauth.account.adapter.DefaultAccountAdapter``).
