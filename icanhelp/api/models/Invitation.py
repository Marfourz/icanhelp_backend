from django.db import models


class InvitationState(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPT", "Accepté"
    REJECTED = "REJECT", "Refusé"
    VALIDATED = "VALIDATE", "Terminé"
    SCHEDULED  = "SCHEDULED",  "RDV confirmé"

    
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
    competence = models.ForeignKey(
        'api.UserCompetence', blank=True, null=True, on_delete=models.CASCADE,
    )
    points = models.PositiveIntegerField(blank=True, default=0)  # ← un seul champ points
    message = models.TextField()
    duration = models.PositiveIntegerField(blank=True, null=True)
    discussion = models.ForeignKey(
        'api.Discussion', blank=True, related_name="invitations", null=True, on_delete=models.PROTECT,
    )
    pointsWasChange = models.BooleanField(default=False, null=True)

    # ── Planification ─────────────────────────────────────────
    scheduledAt    = models.DateTimeField(blank=True, null=True)
    scheduledPlace = models.CharField(max_length=255, blank=True, null=True)
    scheduledBy = models.ForeignKey(
        'api.UserProfil',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='scheduled_invitations'
    )
    validatedByCreator  = models.BooleanField(default=False)
    validatedByReceiver = models.BooleanField(default=False)






    class Meta:
        ordering = ['createdAt']