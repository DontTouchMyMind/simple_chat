from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    async def _send_message(self, data, event=None):
        """Handler for send message to client."""
        await self.send_json(content={
            'status': 'ok',
            'data': data,
            'event': event
        })

    async def _throw_error(self, data, event=None):
        """Handler for throw error to client."""
        await self.send_json(content={
            'status': 'error',
            'data': data,
            'event': event
        })

    async def _group_send(self, data, event=None):
        """The function creates message that will be send to channel layer."""
        data = {
            'type': 'response.proxy',
            'data': data,
            'event': event
        }
        await self.channel_layer.group_send(self.channel, data)

    async def connect(self):
        await self.accept()
        if 'user' not in self.scope or self.scope['user'].is_anonymous:
            await self._send_message({'detail': 'Authorization failed!'})
            await self.close(code=1000)
            return

    async def receive_json(self, content, **kwargs):
        command_from_client = await self.parse_content(content)
        if command_from_client:
            event = command_from_client['event'].replace('.', '_')
            method = getattr(self, f'event_{event}', self.method_undefined)
            await method(command_from_client)
        else:
            await self._throw_error({'detail': 'Invalid message!'})

    async def disconnect(self, code):
        pass

    async def method_undefined(self, message):
        """The function sends to client error message 'Unknown message'."""
        await self._throw_error({'detail': 'Unknown event'}, event=message['event'])

    async def response_proxy(self, event):
        """Handler for send message to the channel layer."""
        await self._send_message(data=event['data'], event=event.get('event'))

    @classmethod
    async def parse_content(cls, content):
        """The method checks if the message valid."""
        if isinstance(content, dict) and isinstance(content.get('event'), str) \
                and isinstance(content.get('data'), dict):
            return content
