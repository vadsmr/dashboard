from unittest.mock import MagicMock, patch

import pytest
from django.db import OperationalError
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_ok() -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.django_db
@patch("apps.core.views.connection.ensure_connection", side_effect=OperationalError)
def test_health_fail(mock_ensure: MagicMock) -> None:
    client = APIClient()
    response = client.get(reverse("health"))

    assert response.status_code == 503
    assert response.json() == {"status": "error"}
    mock_ensure.assert_called_once()
