Advanced Configuration
----------------------

Forcing MFA
'''''''''''''''''''''''''

You can force certain users to use MFA. To enable this, subclass the
``allauth.mfa.middleware.RequireMFAMiddleware`` and implement a
``mfa_required`` method on it. This middleware needs to be added to your
``MIDDLEWARE`` setting.

For example, to require MFA for staff users:

.. code-block:: python

    from allauth.mfa.middleware import RequireMFAMiddleware

    class RequireMFAForStaffMiddleware(RequireMFAMiddleware):
        def mfa_required(self, request):
            return request.user.is_staff

If the (staff) user doesn't have MFA enabled yet, they will be redirected to the MFA setup page and won't be able
to access other pages until they have completed the set-up.

Note that, login, logout, password change and password reset pages always remain accessible.
