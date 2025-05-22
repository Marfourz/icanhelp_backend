from django.db import models
from api.models import UserProfil,Discussion


class UserDiscussionMetaData(models.Model):

    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    lastOpenDiscussionAt = models.DateTimeField(auto_now_add=True)