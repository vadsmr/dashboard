from django.db import connection, OperationalError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        try:
            connection.ensure_connection()
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        except OperationalError:
            return Response({"status": "error"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
