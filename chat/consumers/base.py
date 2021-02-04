from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    async def _send_message(self, data, event=None):
        """Обработчик отправки сообщений клиенту."""
        await self.send_json(content={
            'status': 'ok',
            'data': data,
            'event': event
        })

    async def _throw_error(self, data, event=None):
        """Обработчик отправки ошибки клиенту."""
        await self.send_json(content={
            'status': 'error',
            'data': data,
            'event': event
        })

    async def _group_send(self, data, event=None):
        """Обработчик создания и отправки сообщения в channel layers(в redis)."""
        data = {
            'type': 'response.proxy',
            'data': data,
            'event': event
        }
        await self.channel_layer.group_send(self.channel, data)

    async def connect(self):
        """Метод установки соединения."""
        await self.accept()
        if 'user' not in self.scope or self.scope['user'].is_anonymous:
            await self._send_message({'detail': 'Authorization failed!'})
            await self.close(code=1000)
            return

    async def receive_json(self, content, **kwargs):
        """
        Обработчик сообщений от клиента.
        При получение сообщения от клиента определяет, какой эвент должен обрабатывать сообщение.
        И вызывает соответствующий метод в консьюмере.
        """
        message = await self.parse_content(content)
        if message:
            event = message['event'].replace('.', '_')
            method = getattr(self, f'event_{event}', self.method_undefined)
            await method(message)
        else:
            await self._throw_error({'detail': 'Invalid message!'})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.channel, self.channel_name)
        await super().disconnect(code=code)

    async def method_undefined(self, message):
        """Функция оправляет ошибку, если команда не известна."""
        await self._throw_error({'detail': 'Unknown event'}, event=message['event'])

    async def response_proxy(self, event):
        """Обработчик отправки сообщения всем пользователям, кот. подключены к группе."""
        await self._send_message(data=event['data'], event=event.get('event'))

    @classmethod
    async def parse_content(cls, content):
        """Проверка валидности сообщения."""
        if isinstance(content, dict) and isinstance(content.get('event'), str) and\
                isinstance(content.get('data'), dict):
            return content
