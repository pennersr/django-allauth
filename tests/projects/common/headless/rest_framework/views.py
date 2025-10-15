from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.headless.contrib.rest_framework.authentication import (
    JWTTokenAuthentication,
)


class ResourceView(APIView):
    authentication_classes = [JWTTokenAuthentication]

    def get(self, request, *args, **kwargs):
        data = {"resource": "ok"}
        if "userinfo" in request.GET:
            data["user_email"] = request.user.email
        return Response(data)
