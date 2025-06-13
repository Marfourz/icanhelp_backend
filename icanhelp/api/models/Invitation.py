from django.db import models
from api.models import UserProfil, UserCompetence



class InvitationState(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPT", "Accepté"
    REJECTED = "REJECT", "Refusé"


class Invitation(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    
    createdBy = models.ForeignKey(
        UserProfil, related_name="sendInvitations", blank=False, on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        UserProfil, related_name="receivedInvitations", blank=False, on_delete=models.CASCADE
    )

    state = models.CharField(
        max_length=20,
        choices=InvitationState.choices, 
        default=InvitationState.PENDING
    )

    competences_desired = models.ManyToManyField(
        'UserCompetence', blank=True, related_name="invitation_competences_desired"
    )
    competences_persornal = models.ManyToManyField(
        'UserCompetence',  blank=True, related_name="invitation_competences_personal"
    )

    message = models.TextField()


    class Meta:
        ordering = ['createdAt']