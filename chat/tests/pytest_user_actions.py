import pytest

from chat.models import User


@pytest.mark.django_db
def pytest_creating_users():
    User.objects.create_user(username='test_p_1', email='test_p_1@gmail.com', password='QAZ1598753')
    assert User.objects.count() == 1


@pytest.mark.django_db
def pytest_banned_user():
    new_user = User.objects.create_user(username='test_p_1', email='test_p_1@gmail.com', password='QAZ1598753')
    assert new_user.user_status == 'a'

    new_user.user_status = 'b'
    new_user.save()

    assert new_user.user_status == 'b'
    assert new_user.user_status != 'a'
