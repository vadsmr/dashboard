import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_ok() -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.json() == {"status": "ok"}
