from django.db import models


class InvitationState(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPT", "Accepté"
    REJECTED = "REJECT", "Refusé"
    VALIDATED = "VALIDATE", "Terminé"

class InvitationType(models.TextChoices):
    LEARN = "LEARN", "Learn"
    TEACH = "TEACH", "Teach"

class Invitation(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    
    createdBy = models.ForeignKey(
        'api.UserProfil', related_name="sendInvitations", blank=False, on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        'api.UserProfil', related_name="receivedInvitations", blank=False, on_delete=models.CASCADE
    )

    state = models.CharField(
        max_length=20,
        choices=InvitationState.choices, 
        default=InvitationState.PENDING
    )

    type = models.CharField(
        max_length=20,
        choices=InvitationType.choices,
        default=InvitationType.LEARN
    )

    sender_competence = models.ForeignKey(
        'api.UserCompetence', blank=True, related_name="invitation_competences_send", null=True ,on_delete=models.CASCADE,
    )

    senderPoints = models.PositiveIntegerField(blank=True, null=True)

    receiver_competence = models.ForeignKey(
        'api.UserCompetence',  blank=True, related_name="invitation_competences_receive", null=True ,on_delete=models.CASCADE,
    )

    receiverPoints = models.PositiveIntegerField(blank=True, null=True)

    message = models.TextField()

    duration = models.PositiveIntegerField(blank=True, null=True)

    discussion = models.ForeignKey(
        'api.Discussion',  blank=True, related_name="invitations", null=True ,on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ['createdAt']