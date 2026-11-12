from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User


def test_me_requires_auth(api_client: APIClient) -> None:
    response = api_client.get(reverse('me'))

    assert response.status_code == 403


def test_me_returns_current_user(auth_client: APIClient, user: User) -> None:
    response = auth_client.get(reverse('me'))
    assert response.status_code == 200
    assert response.data['id'] == user.id
    assert response.data['email'] == user.email
    assert set(response.json()) == {
        'id',
        'email',
        'first_name',
        'last_name',
        'date_joined',
    }
