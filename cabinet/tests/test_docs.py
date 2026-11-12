from django.urls import reverse
from rest_framework.test import APIClient


def test_schema_is_public(api_client: APIClient) -> None:
    response = api_client.get(reverse('schema'))
    assert response.status_code == 200
    assert b'openapi:' in response.content
