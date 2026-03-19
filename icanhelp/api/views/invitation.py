
from api.models.Invitation import Invitation, InvitationState, InvitationType
from api.serializers import InvitationSerializer, CreateInvitationSerializer
from api.models.UserProfil import UserProfil
from api.models.Discussion import Discussion
from api.models.Message import Message
from api.serializers import DiscussionSerializer
from api.mixins import UserProfilMixin
from django.db import transaction

from api.models import UserCompetence
from rest_framework import permissions, viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import mixins

class InvitationViewSet(
    UserProfilMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    ):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        userProfil = self.get_user_profil()
        return (
            Invitation.objects.filter(createdBy=userProfil).order_by('-createdAt') |
            Invitation.objects.filter(receiver=userProfil)
        )

    def create(self, request, *args, **kwargs):
        user_profil = get_object_or_404(UserProfil, user=self.request.user)
        receiver_id = request.data.get("receiver")
        competence_id = request.data.get("competence")
        points = int(request.data.get('points', 0))
        type = request.data.get('type')

        if not receiver_id:
            return Response({"message": "Le champ receiver est obligatoire."}, status=400)

        if int(receiver_id) == user_profil.id:
            return Response({"message": "Vous ne pouvez vous envoyer d'invitation."}, status=400)

        if not competence_id:
            return Response({"message": "Le champ compétence est obligatoire."}, status=400)

        receiver_profil = get_object_or_404(UserProfil, id=receiver_id)
        competence = get_object_or_404(UserCompetence, id=competence_id)

        # Vérifier que la compétence appartient bien au receiver
        if type == InvitationType.LEARN:
            if not receiver_profil.get_personal_competences().filter(id=competence_id).exists():
                return Response(
                    {"message": "Le profil ne possède pas les compétences demandées"},
                    status=400
                )

        # Le payeur est le sender si LEARN, le receiver si TEACH
        payer = user_profil if type == InvitationType.LEARN else receiver_profil

        if not payer.has_enough_points(points):
            available = payer.points - payer.pointsToLose
            return Response(
                {"message": f"Points insuffisants. Disponibles : {available}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            discussion = Discussion.get_or_create_between(receiver_profil, user_profil)
            message = request.data.get("message")

            if message:
                msg = Message.objects.create(
                    message=message,
                    discussion=discussion,
                    sender=user_profil
                )
                discussion.lastMessage = msg
                discussion.save()

            serializer = CreateInvitationSerializer(data={
                **request.data,
                'createdBy': user_profil.id,
                'receiver': receiver_profil.id,
                'discussion': discussion.id,
                'competence': competence.id,
                'points': points,
                'pointsWasChanged': points != competence.points
            })

            if not serializer.is_valid():
                return Response(serializer.errors, status=400)

            serializer.save()

        return Response(DiscussionSerializer(discussion).data, status=201)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        invitations = Invitation.objects.filter(createdBy=self.get_user_profil()).order_by('-createdAt')
        return Response(self.get_serializer(invitations, many=True).data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        invitations = Invitation.objects.filter(receiver=self.get_user_profil()).order_by('-createdAt')
        return Response(self.get_serializer(invitations, many=True).data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = get_object_or_404(Invitation, pk=pk)

        if invitation.receiver != self.get_user_profil():
            return Response({"message": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        if invitation.state != InvitationState.PENDING:
            return Response({"message": "Invitation déjà traitée."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            invitation.state = InvitationState.ACCEPTED
            invitation.save()

            invitation.createdBy.accept_invitation(invitation)
            invitation.receiver.accept_invitation(invitation)

        return Response(self.get_serializer(invitation).data, status=status.HTTP_200_OK)

    # ── Proposer un créneau ──────────────────────────────────────
    @action(detail=True, methods=['post'])
    def propose_schedule(self, request, pk=None):
        """
        L'un des deux participants propose une date, heure et lieu.
        L'autre doit confirmer via confirm_schedule.
        """
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state not in [
            InvitationState.ACCEPTED, InvitationState.SCHEDULED
        ]:
            return Response(
                {"message": "L'invitation doit être acceptée pour planifier."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return Response({"message": "Non autorisé."},
                            status=status.HTTP_403_FORBIDDEN)

        scheduled_at    = request.data.get('scheduledAt')
        scheduled_place = request.data.get('scheduledPlace')

        if not scheduled_at:
            return Response({"message": "La date est obligatoire."},
                            status=status.HTTP_400_BAD_REQUEST)

        invitation.scheduledAt    = scheduled_at
        invitation.scheduledPlace = scheduled_place
        invitation.scheduledBy    = user_profil
        # Repasse en ACCEPTED pour que l'autre confirme
        invitation.state = InvitationState.ACCEPTED
        invitation.save(update_fields=[
            'scheduledAt', 'scheduledPlace', 'scheduledBy', 'state'
        ])

        return Response(self.get_serializer(invitation).data)


    # ── Confirmer le créneau proposé ────────────────────────────
    @action(detail=True, methods=['post'])
    def confirm_schedule(self, request, pk=None):
        """
        L'autre participant confirme la proposition de créneau.
        L'invitation passe en SCHEDULED.
        """
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state != InvitationState.ACCEPTED:
            return Response(
                {"message": "Aucun créneau en attente de confirmation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invitation.scheduledBy == user_profil:
            return Response(
                {"message": "Tu ne peux pas confirmer ton propre créneau."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return Response({"message": "Non autorisé."},
                            status=status.HTTP_403_FORBIDDEN)

        invitation.state = InvitationState.SCHEDULED
        invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)


    # ── Valider la séance (double validation) ───────────────────
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Chaque participant valide indépendamment.
        Le transfert de points s'effectue quand les deux ont validé.
        """
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state != InvitationState.SCHEDULED:
            return Response(
                {"message": "La séance doit être confirmée avant validation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return Response({"message": "Non autorisé."},
                            status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            if user_profil == invitation.createdBy:
                invitation.validatedByCreator = True
            else:
                invitation.validatedByReceiver = True

            invitation.save(update_fields=[
                'validatedByCreator', 'validatedByReceiver'
            ])

            # Les deux ont validé → transfert de points
            if invitation.validatedByCreator and invitation.validatedByReceiver:
                invitation.createdBy.validate_invitation(invitation)
                invitation.receiver.validate_invitation(invitation)
                invitation.state = InvitationState.VALIDATED
                invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)


    # ── Rejeter / annuler ────────────────────────────────────────
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Fonctionne depuis PENDING, ACCEPTED et SCHEDULED.
        """
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return Response({"message": "Non autorisé."},
                            status=status.HTTP_403_FORBIDDEN)

        if invitation.state not in [
            InvitationState.PENDING,
            InvitationState.ACCEPTED,
            InvitationState.SCHEDULED,
        ]:
            return Response({"message": "Invitation déjà traitée."},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if invitation.state in [
                InvitationState.ACCEPTED, InvitationState.SCHEDULED
            ]:
                invitation.createdBy.reject_invitation(invitation)
                invitation.receiver.reject_invitation(invitation)

            invitation.state = InvitationState.REJECTED
            invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)