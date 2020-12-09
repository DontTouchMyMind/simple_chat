import pytest
from django.test import Client

from chat.models import User


def create_user(username, email, password):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    return user


@pytest.mark.django_db
def pytest_creating_users():
    new_user = create_user('test_p_1', 'test_p_1@gmail.com', 'QAZ1598753')
    assert User.objects.count() == 1


@pytest.mark.django_db
def pytest_banned_user():
    new_user = create_user('test_p_1', 'test_p_1@gmail.com', 'QAZ1598753')
    assert str(User.objects.filter(username='test_p_1').values('user_status')) == "<QuerySet [{'user_status': 'a'}]>"

    new_user.user_status = 'b'
    new_user.save()

    assert str(User.objects.filter(username='test_p_1').values('user_status')) == "<QuerySet [{'user_status': 'b'}]>"
    assert str(User.objects.filter(username='test_p_1').values('user_status')) != "<QuerySet [{'user_status': 'a'}]>"