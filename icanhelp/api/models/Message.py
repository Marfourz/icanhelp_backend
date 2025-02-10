from django.db import models
from api.models.Discussion import Discussion


class Message(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="messages")
    class Meta:
        ordering = ['created']