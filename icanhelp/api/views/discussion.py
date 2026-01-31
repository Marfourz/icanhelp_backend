
from rest_framework import viewsets, status,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Discussion, Message
from api.serializers import DiscussionSerializer, MessageSerializer
from api.mixins import UserProfilMixin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from django.db.models import OuterRef, Subquery
from rest_framework import mixins


from api.models import UserDiscussionMetaData


class DiscussionViewSet(
    UserProfilMixin, 
    viewsets.GenericViewSet,
    mixins.ListModelMixin
):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Récupérer uniquement les discussions où l'utilisateur est impliqué """

        user_profil = self.get_user_profil()    
        # Sous-requête pour récupérer la dernière ouverture de la discussion par l'utilisateur
        discussions = Discussion.objects.annotate(
            lastOpenAt=Subquery(
            UserDiscussionMetaData.objects.filter(
                user=user_profil,
                discussion=OuterRef('pk')
            ).values("lastOpenDiscussionAt")[:1],
        )
        ).filter(users__id=user_profil.id)

        

        for d in discussions:
            d.nbMessagesNotRead = d.messages.filter(createdAt__gt=(d.lastOpenAt or datetime(1970, 1, 1))).filter(~Q(sender=user_profil)).count()

        return discussions
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """ Récupérer les messages d'une discussion """
        user_profil = self.get_user_profil()
        discussion = get_object_or_404(Discussion, pk=pk, users=user_profil)
        messages = discussion.messages.order_by('-createdAt')   
        serializer = MessageSerializer(messages, many=True)
        try:
            userDiscussionMetaData = UserDiscussionMetaData.objects.get(discussion=discussion, user=user_profil)
        except:
            userDiscussionMetaData= UserDiscussionMetaData.objects.create(discussion=discussion, user=user_profil)
        userDiscussionMetaData.lastOpenDiscussionAt = datetime.now()
        userDiscussionMetaData.save()
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
                    "id": message.id,
                    'discussion_id':  discussion.id
                }
            )
           
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
