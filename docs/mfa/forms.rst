Forms
=====

Authenticate/Reauthenticate
***************************

*Path*
  ``allauth.mfa.forms.AuthenticateForm``

*Used on*:
  AuthenticateView and ReauthenticateView used when a user authenticates with MFA.

Example override::

    from allauth.mfa.forms import AuthenticateForm
    class MyCustomAuthenticateForm(AuthenticateForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'authenticate': 'mysite.forms.MyCustomAuthenticateForm',
        'reauthenticate': 'mysite.forms.MyCustomAuthenticateForm',
    }

Activate TOTP
************

*Path*
  ``allauth.mfa.forms.ActivateTOTPForm``

*Used on*:
  ActivateTOTPView used when a user activates TOTP.

Example override::

    from allauth.mfa.forms import ActivateTOTPForm
    class MyCustomActivateTOTPForm(ActivateTOTPForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'activatetotp': 'mysite.forms.MyCustomActivateTOTPForm',
    }

Deactivate TOTP
**************

*Path*
  ``allauth.mfa.forms.DeactivateTOTPForm``

*Used on*:
  DeactivateTOTPView used when a user deactivates TOTP.

Example override::

    from allauth.mfa.forms import DeactivateTOTPForm
    class MyCustomDeactivateTOTPForm(DeactivateTOTPForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'deactivatetotp': 'mysite.forms.MyCustomDeactivateTOTPForm',
    }

Generate Recovery Codes
**************

*Path*
  ``allauth.mfa.forms.GenerateRecoveryCodesForm``

*Used on*:
  GenerateRecoveryCodesView used when a user generates recovery codes.

Example override::

    from allauth.mfa.forms import GenerateRecoveryCodesForm
    class MyCustomGenerateRecoveryCodesForm(GenerateRecoveryCodesForm):
      pass

``settings.py``::

    MFA_FORMS = {
        'generate_recovery_codes': 'mysite.forms.MyCustomGenerateRecoveryCodesForm',
    }
