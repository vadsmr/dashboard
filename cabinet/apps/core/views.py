from django.db import OperationalError, connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(
    responses={
        200: OpenApiResponse(description='Database is reachable'),
        503: OpenApiResponse(description='Database is unavailable'),
    }
)
class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        try:
            connection.ensure_connection()
        except OperationalError:
            return Response({'status': 'error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'status': 'ok'})
