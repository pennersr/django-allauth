from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.headless.contrib.rest_framework.authentication import (
    XSessionTokenAuthentication,
)

from .serializers import AddSerializer


class AddAPIView(APIView):
    authentication_classes = [
        authentication.SessionAuthentication,
        XSessionTokenAuthentication,
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = AddSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(
            data={
                "result": serializer.validated_data["x"]
                + serializer.validated_data["y"]
            }
        )
