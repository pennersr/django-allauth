from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.idp.oidc.contrib.rest_framework.authentication import TokenAuthentication
from allauth.idp.oidc.contrib.rest_framework.permissions import TokenPermission


class ResourceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [TokenPermission.has_scope(["view-resource"])]

    def get(self, request, *args, **kwargs):
        return Response({"resource": "ok", "user_email": request.user.email})
