Forms
=====

(Re)authenticate
****************

*Path*
  ``allauth.mfa.base.forms.AuthenticateForm``
  ``allauth.mfa.base.forms.ReauthenticateForm``

*Used on*:
  AuthenticateView and ReauthenticateView, used when a user authenticates with MFA.

Example override::

    from allauth.mfa.base.forms import AuthenticateForm, ReauthenticateForm
    class MyCustomAuthenticateForm(AuthenticateForm):
      pass

    class MyCustomReauthenticateForm(ReauthenticateForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'authenticate': 'mysite.forms.MyCustomAuthenticateForm',
        'reauthenticate': 'mysite.forms.MyCustomReauthenticateForm',
    }

Activate TOTP
*************

*Path*
  ``allauth.mfa.totp.forms.ActivateTOTPForm``

*Used on*:
  ActivateTOTPView, used when a user activates TOTP.

Example override::

    from allauth.mfa.totp.forms import ActivateTOTPForm
    class MyCustomActivateTOTPForm(ActivateTOTPForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'activate_totp': 'mysite.forms.MyCustomActivateTOTPForm',
    }

Deactivate TOTP
***************

*Path*
  ``allauth.mfa.totp.forms.DeactivateTOTPForm``

*Used on*:
  DeactivateTOTPView, used when a user deactivates TOTP.

Example override::

    from allauth.mfa.totp.forms import DeactivateTOTPForm
    class MyCustomDeactivateTOTPForm(DeactivateTOTPForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'deactivate_totp': 'mysite.forms.MyCustomDeactivateTOTPForm',
    }

Generate Recovery Codes
***********************

*Path*
  ``allauth.mfa.recovery_codes.forms.GenerateRecoveryCodesForm``

*Used on*:
  GenerateRecoveryCodesView, used when a user generates recovery codes.

Example override::

    from allauth.mfa.recovery_codes.forms import GenerateRecoveryCodesForm
    class MyCustomGenerateRecoveryCodesForm(GenerateRecoveryCodesForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'generate_recovery_codes': 'mysite.forms.MyCustomGenerateRecoveryCodesForm',
    }
