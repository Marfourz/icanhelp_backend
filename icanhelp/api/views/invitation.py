from api.models.Invitation import Invitation, InvitationState, InvitationType
from api.serializers import InvitationSerializer, CreateInvitationSerializer
from api.models.UserProfil import UserProfil
from api.models.Discussion import Discussion
from api.models.Message import Message
from api.serializers import DiscussionSerializer
from api.mixins import UserProfilMixin
from api.utils.errors import ErrorCode, api_error, validation_error
from django.db import transaction

from api.models import UserCompetence
from rest_framework import permissions, viewsets, status
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
        user_profil = self.get_user_profil()
        return (
            Invitation.objects.filter(createdBy=user_profil).order_by('-createdAt') |
            Invitation.objects.filter(receiver=user_profil)
        )

    def create(self, request, *args, **kwargs):
        user_profil = get_object_or_404(UserProfil, user=self.request.user)
        receiver_id = request.data.get("receiver")
        competence_id = request.data.get("competence")
        inv_type = request.data.get('type')

        if not receiver_id:
            return api_error(ErrorCode.RECEIVER_REQUIRED, "Le champ destinataire est obligatoire.")

        if int(receiver_id) == user_profil.id:
            return api_error(ErrorCode.INVITATION_SELF, "Vous ne pouvez pas vous envoyer une invitation.")

        if not competence_id:
            return api_error(ErrorCode.COMPETENCE_REQUIRED, "Le champ compétence est obligatoire.")

        receiver_profil = get_object_or_404(UserProfil, id=receiver_id)
        competence = get_object_or_404(UserCompetence, id=competence_id)
        points = competence.points or 0

        if inv_type == InvitationType.LEARN:
            if not receiver_profil.get_personal_competences().filter(id=competence_id).exists():
                return api_error(
                    ErrorCode.COMPETENCE_NOT_OWNED,
                    "Ce profil ne possède pas la compétence demandée."
                )

        payer = user_profil if inv_type == InvitationType.LEARN else receiver_profil
        if not payer.has_enough_points(points):
            available = payer.points - payer.pointsToLose
            return api_error(
                ErrorCode.INSUFFICIENT_POINTS,
                f"Points insuffisants. Disponibles : {available}",
                detail={"available": available},
            )

        with transaction.atomic():
            discussion = Discussion.get_or_create_between(receiver_profil, user_profil)
            message_text = request.data.get("message")

            if message_text:
                msg = Message.objects.create(
                    message=message_text,
                    discussion=discussion,
                    sender=user_profil,
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
                'pointsWasChanged': False,
            })

            if not serializer.is_valid():
                return validation_error(serializer.errors)

            serializer.save()

        return Response(DiscussionSerializer(discussion).data, status=status.HTTP_201_CREATED)

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
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé à accepter cette invitation.", status=status.HTTP_403_FORBIDDEN)

        if invitation.state != InvitationState.PENDING:
            return api_error(ErrorCode.INVITATION_ALREADY_PROCESSED, "Cette invitation a déjà été traitée.")

        with transaction.atomic():
            invitation.state = InvitationState.ACCEPTED
            invitation.save()
            invitation.createdBy.accept_invitation(invitation)
            invitation.receiver.accept_invitation(invitation)

        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=['post'])
    def propose_schedule(self, request, pk=None):
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state not in [InvitationState.ACCEPTED, InvitationState.SCHEDULED]:
            return api_error(
                ErrorCode.INVITATION_NOT_ACCEPTED,
                "L'invitation doit être acceptée pour planifier une séance."
            )

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)

        if not request.data.get('scheduledAt'):
            return api_error(ErrorCode.SCHEDULE_DATE_REQUIRED, "La date de la séance est obligatoire.")

        invitation.scheduledAt    = request.data.get('scheduledAt')
        invitation.scheduledPlace = request.data.get('scheduledPlace')
        invitation.scheduledBy    = user_profil
        invitation.state = InvitationState.ACCEPTED
        invitation.save(update_fields=['scheduledAt', 'scheduledPlace', 'scheduledBy', 'state'])

        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=['post'])
    def confirm_schedule(self, request, pk=None):
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state != InvitationState.ACCEPTED:
            return api_error(ErrorCode.INVITATION_NO_PENDING_SCHEDULE, "Aucun créneau en attente de confirmation.")

        if invitation.scheduledBy == user_profil:
            return api_error(ErrorCode.SCHEDULE_SELF_CONFIRM, "Vous ne pouvez pas confirmer votre propre proposition.")

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)

        invitation.state = InvitationState.SCHEDULED
        invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if invitation.state != InvitationState.SCHEDULED:
            return api_error(ErrorCode.INVITATION_NOT_SCHEDULED, "La séance doit être confirmée avant de pouvoir la valider.")

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)

        already_validated = (
            (user_profil == invitation.createdBy and invitation.validatedByCreator) or
            (user_profil == invitation.receiver and invitation.validatedByReceiver)
        )
        if already_validated:
            return api_error(ErrorCode.INVITATION_ALREADY_PROCESSED, "Vous avez déjà validé cette séance.")

        with transaction.atomic():
            if user_profil == invitation.createdBy:
                invitation.validatedByCreator = True
            else:
                invitation.validatedByReceiver = True

            invitation.save(update_fields=['validatedByCreator', 'validatedByReceiver'])

            if invitation.validatedByCreator and invitation.validatedByReceiver:
                invitation.createdBy.validate_invitation(invitation)
                invitation.receiver.validate_invitation(invitation)
                invitation.state = InvitationState.VALIDATED
                invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        invitation = get_object_or_404(Invitation, pk=pk)
        user_profil = self.get_user_profil()

        if user_profil not in [invitation.createdBy, invitation.receiver]:
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)

        if invitation.state not in [InvitationState.PENDING, InvitationState.ACCEPTED, InvitationState.SCHEDULED]:
            return api_error(ErrorCode.INVITATION_ALREADY_PROCESSED, "Cette invitation a déjà été traitée.")

        with transaction.atomic():
            if invitation.state in [InvitationState.ACCEPTED, InvitationState.SCHEDULED]:
                invitation.createdBy.reject_invitation(invitation)
                invitation.receiver.reject_invitation(invitation)
            invitation.state = InvitationState.REJECTED
            invitation.save(update_fields=['state'])

        return Response(self.get_serializer(invitation).data)
