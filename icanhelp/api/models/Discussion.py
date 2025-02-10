from django.db import models
from api.models.UserProfil import UserProfil

STATES = [
        ('PENDING', 'En attente'),
        ('ACCEPT', 'Accepté'),
        ('REJECT', 'Refusé'),
]


class Discussion(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100,default='')
    
    createdBy = models.ForeignKey(
        UserProfil, related_name="createDiscussions", blank=False, on_delete=models.CASCADE,
    )

    user2 = models.ForeignKey(
        UserProfil, related_name="receivedDiscussions", blank=False, on_delete=models.CASCADE
    )

    state = models.CharField(max_length=20, choices=STATES, default='PENDING')


    class Meta:
        ordering = ['created']