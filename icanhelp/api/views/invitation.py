
from api.models.Invitation import Invitation, InvitationState
from api.serializers import InvitationSerializer, CreateInvitationSerializer
from api.models.UserProfil import UserProfil
from api.models.Discussion import Discussion
from api.models.Message import Message
from api.serializers import DiscussionSerializer
from api.mixins import UserProfilMixin
 

from rest_framework import permissions, viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from api.models import UserCompetence


class InvitationViewSet(UserProfilMixin,viewsets.ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        """Permet à un utilisateur de voir uniquement ses invitations (envoyées ou reçues)."""
        userProfil = self.get_user_profil()
        query = Invitation.objects.filter(createdBy=userProfil).order_by('-createdAt') | Invitation.objects.filter(receiver=userProfil)

        return query

    
    def create(self, request, *args, **kwargs):
        """Override de la méthode create pour forcer l'assignation de createdBy."""
        user_profil = get_object_or_404(UserProfil, user=self.request.user)
        
        # Récupérer le receiver de la requête
        receiver_id = request.data.get("receiver")

        message = request.data.get("message")

        receiverCompetence = request.data.get('receiver_competence')

        if not user_profil.get_personal_competences().filter(id=receiverCompetence).exists():
            return Response(
                    {"message": "Le profil ne possède pas les compétences demandées"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not receiver_id:
            return Response({"message": "Le champ receiver est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Assigner receiver en fonction de l'ID fourni
        receiver_profil = get_object_or_404(UserProfil, id=receiver_id)

        if receiver_id == user_profil.id:
            return Response({"message": "Vous ne pouvez vous envoyer d'invitation."}, status=status.HTTP_400_BAD_REQUEST)

        discussion = Discussion.get_or_create_between(receiver_profil, user_profil)

         # Création du premier message avec le texte de l'invitation
        if message: 
            message = Message.objects.create(
                message=message,
                discussion=discussion,
                sender=user_profil
            )

            discussion.lastMessage = message

            discussion.save()

        invitation_data = {
            **request.data,
            'createdBy': user_profil.id,
            'receiver': receiver_profil.id,
            'discussion': discussion.id,
        }

        serializer = CreateInvitationSerializer(data=invitation_data)

        if serializer.is_valid():
            serializer.save()
        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        discussion_serializer = DiscussionSerializer(discussion)

        return Response(discussion_serializer.data, status=status.HTTP_201_CREATED)
        

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Lister les invitations envoyées par l'utilisateur."""
        invitations = Invitation.objects.filter(createdBy=self.get_user_profil()).order_by('-createdAt')
        serializer = self.get_serializer(invitations, many=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Lister les invitations reçues par l'utilisateur."""
        invitations = Invitation.objects.filter(receiver=self.get_user_profil()).order_by('-createdAt')
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accepter une invitation et créer une discussion."""
        invitation = get_object_or_404(Invitation, pk=pk)

        if invitation.receiver != self.get_user_profil():
            return Response(
                {"message": "Vous n'êtes pas autorisé à accepter cette invitation."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Mise à jour du statut de l'invitation
        invitation.state = InvitationState.ACCEPTED
        invitation.save()

        sender = invitation.createdBy
        receiver = self.get_user_profil()

       # Mise à jour du sender
        sender.update_points_after_invitation(
            points_to_win=invitation.senderPoints,
            points_to_lose=invitation.receiverPoints,
            is_sender=True
        )

        # Mise à jour du receiver
        receiver.update_points_after_invitation(
            points_to_win=invitation.receiverPoints,
            points_to_lose=invitation.senderPoints,
            is_sender=False
        )
        
        # Création de la discussion
        discussion = Discussion.get_or_create_between(sender, receiver)

        # Création du premier message avec le texte de l'invitation
        if invitation.message: 
            message = Message.objects.create(
                message=invitation.message,
                discussion=discussion,
                sender=invitation.createdBy
            )

            discussion.lastMessage = message

            discussion.save()

        # Sérialisation et réponse avec la discussion
        discussion_serializer = DiscussionSerializer(discussion)


    
        return Response(discussion_serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Refuser une invitation."""
        invitation = get_object_or_404(Invitation, pk=pk)

        sender = invitation.createdBy
        receiver = invitation.receiver

        if sender !=self.get_user_profil():
            return Response(
                {"message": "Vous n'êtes pas autorisé à valider cette invitation."},
                status=status.HTTP_403_FORBIDDEN
            )

       # Mise à jour du sender
        sender.pointsToLose -= invitation.receiverPoints
        sender.save(update_fields=["pointsToLose"])

        # Mise à jour du receiver
        receiver.pointsToWin -= invitation.receiverPoints
        receiver.points += invitation.receiverPoints
        receiver.save(update_fields=["pointsToWin", "points"])

        invitation.state = InvitationState.VALIDATE
        invitation.save()

        serializer = self.get_serializer(invitation)
        return Response(serializer.data)
    
   
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Refuser une invitation."""
        invitation = get_object_or_404(Invitation, pk=pk)

        if invitation.receiver !=self.get_user_profil():
            return Response(
                {"message": "Vous n'êtes pas autorisé à refuser cette invitation."},
                status=status.HTTP_403_FORBIDDEN
            )

        invitation.state = InvitationState.REJECTED
        invitation.save()

        serializer = self.get_serializer(invitation)
        return Response(serializer.data)
    