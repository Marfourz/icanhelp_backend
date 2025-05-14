from django.db import models
from api.models.UserProfil import UserProfil


class Discussion(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100,default='')
    
    createdBy = models.ForeignKey(
        UserProfil, related_name="createDiscussions", blank=False, on_delete=models.CASCADE,
    )

    users = models.ManyToManyField(
        UserProfil, blank=True, related_name="discussions"
    )

    lastMessage = models.ForeignKey(
        'api.Message', blank=True, on_delete=models.SET_NULL,null=True,related_name="discussion_of_last"
    )

    class Meta:
        ordering = ['createdAt']