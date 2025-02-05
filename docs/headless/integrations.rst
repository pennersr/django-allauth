Integrations
============

When using allauth headless in non-browser contexts, such as mobile apps, a
session token is used to keep track of the authentication state. This session
token is handed over by the app by providing the ``X-Session-Token`` request
header.

Once a user authenticates, you can hand out your own type of token by setting up
a specific :doc:`tokens`. However, if you do not have any requirements that
prescribe a specific token strategy, you can also opt to use the same
authentication strategy that allauth is using. In order to do so, integration
with Django Ninja and Django REST framework is offered out of the box.


Django Ninja
------------

For Django Ninja, the following security class is available:

.. autoclass:: allauth.headless.contrib.ninja.security.XSessionTokenAuth
   :members:

An example on how to use that security class in your own code is listed below:

.. code-block:: python

    from allauth.headless.contrib.ninja.security import x_session_token_auth
    from ninja import NinjaAPI

    api = NinjaAPI()

    @api.get("/your/own/api", auth=[x_session_token_auth])
    def your_own_api(request):
        ...




Django REST framework
---------------------

For Django REST framework, the following authentication class is available:

.. autoclass:: allauth.headless.contrib.rest_framework.authentication.XSessionTokenAuthentication
   :members:

An example on how to use that authentication class in your own code is listed below:

.. code-block:: python

    from allauth.headless.contrib.rest_framework.authentication import (
        XSessionTokenAuthentication,
    )
    from rest_framework import permissions
    from rest_framework.views import APIView

    class YourOwnAPIView(APIView):

        authentication_classes = [
            XSessionTokenAuthentication,
        ]
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request):
            ...
