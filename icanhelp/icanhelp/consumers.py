import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from rest_framework.exceptions import AuthenticationFailed

from api.models import Discussion

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Vérifiez que channel_layer est initialisé
        self.channel_layer = get_channel_layer()

        
       # Vérifier si l'utilisateur est authentifié via le token
        token_key = self.scope.get('query_string').decode('utf-8').split('=')[1]

        self.scope['user'] = await self.get_user_from_token(token_key)


        if self.scope['user'] is None:
            await self.close()
            return
        
        # Vérifier si l'utilisateur fait partie de la discussion
        discussion = await self.get_discussion(self.room_name, self.scope['user'])

        if discussion is None:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(text_data, "aaaaaaaaaaaaaaaaaaaaa")
        text_data_json = json.loads(text_data)
        
        message = text_data_json['message']
        sender = text_data_json['sender']
        id = text_data_json['id']
        

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender' : sender,
                'id': id
            }
        )

    async def chat_message(self, event):
        id = event['id']
        sender = event['sender']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'id': id,
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            access_token = AccessToken(token_key)
            return access_token.payload.get('user_id')
        except Exception as e:
            raise AuthenticationFailed('Invalid token')

    @database_sync_to_async
    def get_discussion(self, room_name, user_id):
        try:
            return Discussion.objects.filter(users=user_id).get(pk=room_name)
        except Discussion.DoesNotExist:
            return None
