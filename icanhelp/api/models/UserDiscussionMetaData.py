from django.db import models
from django.utils import timezone


class UserDiscussionMetaData(models.Model):

    user = models.ForeignKey('api.UserProfil', on_delete=models.CASCADE)
    discussion = models.ForeignKey('api.Discussion', on_delete=models.CASCADE)
    lastOpenDiscussionAt = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'discussion')