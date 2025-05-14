from django.db import models
from api.models.Discussion import Discussion
from api.models.UserProfil import UserProfil



class MessageType(models.TextChoices):
    TEXT = "text"
    IMAGE = "Image"
    FILE = "File"


class Message(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=MessageType.choices, 
        default=MessageType.TEXT
    )
    sender = models.ForeignKey(
        UserProfil, related_name="messageSends", blank=True, null=True ,on_delete=models.CASCADE,
    ) 
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="messages")
    class Meta:
        ordering = ['createdAt']