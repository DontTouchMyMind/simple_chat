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
async def pytest_group_consumer():
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

    # Test group_list method.
    await communicator.send_json_to({'event': 'group.list', 'data': {}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'ok'
    assert result['event'] == 'group.list'
    assert len(result['data']) == 0

    # Test user list method.
    await communicator.send_json_to({'event': 'user.list', 'data': {}})
    result = await communicator.receive_json_from()
    assert result['status'] == 'ok'
    assert result['event'] == 'user.list'
    assert len(result['data']) == 0     # Without new_user!

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def pytest_chat_consumer():
    client1 = Client()
    client2 = Client()

    user1 = await create_user('test_p_1', 'test_p_1@gmail.com', 'QAZ1598753')
    user2 = await create_user('test_p_2', 'test_p_2@gmail.com', 'QAZ1598753')
    client1.force_login(user=user1)
    client2.force_login(user=user2)

    communicator1 = WebsocketCommunicator(
        application=application,
        path='/ws/groups/',
        headers=[(
            b'cookie',
            f'sessionid={client1.cookies["sessionid"].value}'.encode('ascii')
        )]
    )
    connected, _ = await communicator1.connect()
    assert connected

    # Group creation test.
    await communicator1.send_json_to({"event": "group.create", "data": {"name": "Group P1"}})
    message = await communicator1.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'group.create'
    assert message['data']['name'] == 'Group P1'
    group_url = message['data']['link']
    await communicator1.disconnect()

    communicator1 = WebsocketCommunicator(
        application=application,
        path=group_url,
        headers=[(
            b'cookie',
            f'sessionid={client1.cookies["sessionid"].value}'.encode('ascii')
        )]
    )
    connected1, _ = await communicator1.connect()
    assert connected1

    communicator2 = WebsocketCommunicator(
        application=application,
        path=group_url,
        headers=[(
            b'cookie',
            f'sessionid={client2.cookies["sessionid"].value}'.encode('ascii')
        )]
    )
    connected2, _ = await communicator2.connect()
    assert connected2

    # Test add participant.
    await communicator1.send_json_to({"event": "add.participant", "data": {"user_id": user2.id}})
    message = await communicator1.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'add.participant'
    assert len(message['data']) == 2

    # Test send message to group.
    await communicator1.send_json_to({"event": "send.message", "data": {"message": "hello from pytest"}})
    message = await communicator1.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'send.message'
    assert message['data']['message'] == 'hello from pytest'

    # Test receive message form group.
    message = await communicator2.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'send.message'
    assert message['data']['message'] == 'hello from pytest'
    await communicator2.disconnect()

    communicator2 = WebsocketCommunicator(
        application=application,
        path=group_url,
        headers=[(
            b'cookie',
            f'sessionid={client2.cookies["sessionid"].value}'.encode('ascii')
        )]
    )

    connected2, _ = await communicator2.connect()
    assert connected2

    # Test send/receive message after reconnect.
    await communicator1.send_json_to({"event": "send.message", "data": {"message": "hello 2 from pytest"}})
    message = await communicator1.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'send.message'
    assert message['data']['message'] == 'hello 2 from pytest'

    message = await communicator2.receive_json_from()
    assert message['status'] == 'ok'
    assert message['event'] == 'send.message'
    assert message['data']['message'] == 'hello 2 from pytest'

    await communicator1.disconnect()
    await communicator2.disconnect()