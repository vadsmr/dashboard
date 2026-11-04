import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_create_user() -> None:
    user = User.objects.create_user(email='Vadim@Example.COM', password='secret-pass')

    assert user.email == 'Vadim@example.com'
    assert user.check_password('secret-pass')
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_superuser() -> None:
    user = User.objects.create_superuser(email='Vadim@Example.COM', password='secret-pass')

    assert user.email == 'Vadim@example.com'
    assert user.check_password('secret-pass')
    assert user.is_staff
    assert user.is_superuser


def test_create_user_with_empty_email() -> None:
    with pytest.raises(ValueError, match='Email is required'):
        User.objects.create_user(email='', password='secret-pass')


@pytest.mark.django_db
def test_create_user_with_same_email() -> None:
    User.objects.create_user(email='vadim@Example.COM', password='secret-pass')

    with pytest.raises(IntegrityError):
        User.objects.create_user(email='VADIM@Example.COM', password='secret-pass')
