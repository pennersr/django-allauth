Frequently Asked Questions
==========================

My signup requires additional inputs, is that supported?
--------------------------------------------------------

Yes, though an important thing to keep in mind is that there is no one-to-one
mapping of headed forms to headless input payloads. For example, while having to
enter your password twice makes sense in a headed environment, it is pointless
from an API point of view.  As a result, the headed forms that can be overridden
by means of ``ACCOUNT_FORMS`` play no role in the headless environment.

Instead of overriding the complete signup form via ``ACCOUNT_FORMS``, provide a
``ACCOUNT_SIGNUP_FORM_CLASS`` that derives from ``forms.Form`` and only lists
the additional fields you need. These fields will automatically show up in the
headed signup form, and will automatically be validated when posting payloads to
the signup endpoint.
