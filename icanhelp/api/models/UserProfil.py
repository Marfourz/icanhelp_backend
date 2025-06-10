from django.contrib.auth.models import User
from django.db import models
from api.models import Competence, UserCompetence



class UserProfil(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profil")

    competences_desired = models.ManyToManyField(
        'UserCompetence', blank=True, related_name="user_desired"
    )
    competences_persornal = models.ManyToManyField(
        'UserCompetence',  blank=True, related_name="user_personal"
    )
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    points = models.PositiveIntegerField(default=10)
    availability = models.JSONField(default=dict)

    def __str__(self):
        return self.user.username
    
