import pytest
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
def test_health_ok() -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.json() == {"status": "ok"}
