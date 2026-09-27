from django.db import models


class PlaceType(models.TextChoices):
    IN_PERSON = "IN_PERSON", "En personne"
    ONLINE    = "ONLINE",    "En ligne"
    FLEXIBLE  = "FLEXIBLE",  "Flexible"


class Availability(models.Model):
    user      = models.ForeignKey('api.UserProfil', related_name='availabilities', on_delete=models.CASCADE)
    dayOfWeek = models.IntegerField()
    startTime = models.TimeField()
    endTime   = models.TimeField()
    placeType = models.CharField(max_length=20, choices=PlaceType.choices, default=PlaceType.FLEXIBLE)
    place     = models.CharField(max_length=255, blank=True, null=True)
    link      = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['dayOfWeek', 'startTime']
        unique_together = [('user', 'dayOfWeek', 'startTime', 'endTime')]
