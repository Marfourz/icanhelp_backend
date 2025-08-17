from django.db import models

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
        'api.UserProfil', related_name="messageSends", blank=True, null=True ,on_delete=models.CASCADE,
    ) 
    discussion = models.ForeignKey('api.Discussion', on_delete=models.CASCADE, related_name="messages")
    class Meta:
        ordering = ['createdAt']