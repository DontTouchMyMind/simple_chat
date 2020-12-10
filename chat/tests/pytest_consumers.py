import pytest

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import Client


from chat.models import User
from simple_chat.routing import application


@database_sync_to_async
def create_user(username, email, password):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    return user


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def pytest_consumers():
    client = Client()
    new_user = await create_user('test_p_1', 'test_p_1@gmail.com', 'QAZ1598753')
    client.force_login(user=new_user)

    communicator = WebsocketCommunicator(
        application=application,
        path='/ws/groups/',
        headers=[(
            b'cookie',
            f'sessionid={client.cookies["sessionid"].value}'.encode('ascii')
        )]
    )
    connected, _ = await communicator.connect()
    # Connection test.
    assert connected

    # Test parse content.
    await communicator.send_json_to({'event': '', 'data': ''})  # 'data' is dict.
    result = await communicator.receive_json_from()
    assert result['status'] == 'error'
    assert result['data']['detail'] == 'Invalid message!'

    # Test method undefined.
    await communicator.send_json_to({'event': 'undefined.method', 'data': {}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'error'
    assert result['event'] == 'undefined.method'
    assert result['data']['detail'] == 'Unknown event'

    # Group creation test.
    await communicator.send_json_to({'event': 'group.create', 'data': {'name': 'Group 1'}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'ok'
    assert result['event'] == 'group.create'
    assert result['data']['name'] == 'Group 1'

    # Test group_list method.
    await communicator.send_json_to({'event': 'group.list', 'data': {}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'ok'
    assert result['event'] == 'group.list'
    assert len(result['data']) == 1

    # Test user list method.
    await communicator.send_json_to({'event': 'user.list', 'data': {}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'ok'
    assert result['event'] == 'user.list'
    assert len(result['data']) == 0 # Т.к. исключается пользователь, создавший запрос.

    await communicator.disconnect()
