from unittest.mock import patch

import pytest
from django.db import OperationalError
from django.urls import reverse
from rest_framework.test import APIClient


def mock_connection() -> None:
    raise OperationalError()

@pytest.mark.django_db
def test_health_ok() -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("django.db.connection.ensure_connection", mock_connection)
@pytest.mark.django_db
def test_health_fail() -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.status_code == 503
    assert response.json() == {"status": "error"}
