Integrations
============

In order to simplify implementing your own OIDC based API endpoints, allauth
offers out of the box support for authenticating and authorizing requests with
Django Ninja as well as Django REST framework.


Django Ninja
------------

For Django Ninja, the following security class is available:

.. autoclass:: allauth.idp.oidc.contrib.ninja.security.TokenAuth
   :special-members: __init__
   :members:

An example on how to use that security class in your own code is listed below:

.. code-block:: python

    from allauth.idp.oidc.contrib.ninja.security import TokenAuth
    from ninja import NinjaAPI

    api = NinjaAPI()

    @api.get("/api/resource", auth=[TokenAuth(scope=["view-resource"])])
    def resource(request):
        ...




Django REST framework
---------------------

For Django REST framework, the following authentication class is available:

.. autoclass:: allauth.idp.oidc.contrib.rest_framework.authentication.TokenAuthentication

.. autoclass:: allauth.idp.oidc.contrib.rest_framework.permissions.TokenPermission
   :members: has_scope

An example on how to use that authentication class in your own code is listed below:

.. code-block:: python

    from rest_framework.views import APIView

    from allauth.idp.oidc.contrib.rest_framework.authentication import TokenAuthentication
    from allauth.idp.oidc.contrib.rest_framework.permissions import TokenPermission


    class ResourceView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [TokenPermission.has_scope(["view-resource"])]

        def get(request, *args, **kwargs):
            ...
