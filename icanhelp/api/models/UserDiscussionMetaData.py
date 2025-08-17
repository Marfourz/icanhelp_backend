from django.db import models


class UserDiscussionMetaData(models.Model):

    user = models.ForeignKey('api.UserProfil', on_delete=models.CASCADE)
    discussion = models.ForeignKey('api.Discussion', on_delete=models.CASCADE)
    lastOpenDiscussionAt = models.DateTimeField(auto_now_add=True)