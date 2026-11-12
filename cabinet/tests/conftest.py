import pytest
from rest_framework.test import APIClient

from apps.users.models import User

from .factories import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return UserFactory()


@pytest.fixture
def auth_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client
