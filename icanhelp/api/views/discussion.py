from api.models import UserProfil
from rest_framework import viewsets, status,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Discussion, Message
from api.serializers import DiscussionSerializer, MessageSerializer
from api.mixins import UserProfilMixin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class DiscussionViewSet(UserProfilMixin, viewsets.ModelViewSet):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Récupérer uniquement les discussions où l'utilisateur est impliqué """
        return Discussion.objects.filter(users=self.get_user_profil()).order_by('-createdAt')

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """ Récupérer les messages d'une discussion """
        user_profil = self.get_user_profil()
        discussion = get_object_or_404(Discussion, pk=pk, users=user_profil)
        messages = discussion.messages.order_by('-createdAt')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """ Envoyer un message dans une discussion """
        user_profil = self.get_user_profil()
        discussion = get_object_or_404(Discussion, pk=pk, users=user_profil)
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            message = serializer.save(discussion=discussion, sender=user_profil)
            discussion.lastMessage = message
            discussion.save()
            # Envoyer le message via WebSocket
            channel_layer = get_channel_layer()
           
            async_to_sync(channel_layer.group_send)(
                'chat_' + str(discussion.id),
                {
                    "type": "chat_message",
                    "message": message.message,
                    "sender": user_profil.id,
                    "id": message.id
                }
            )
           
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
