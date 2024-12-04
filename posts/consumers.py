# posts/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Post, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Unirse a la sala de grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceptar la conexión WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Dejar la sala de grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje desde WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enviar mensaje a la sala de grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Recibir mensaje desde la sala de grupo
    async def chat_message(self, event):
        message = event['message']

        # Enviar mensaje a WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
