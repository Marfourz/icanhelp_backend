from django.contrib.auth.models import User
from django.db import models

from api.models.UserCompetence import CompetenceType


class UserProfil(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profil")
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    adress = models.CharField(max_length=100, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    points = models.PositiveIntegerField(default=10)
    pointsToWin = models.PositiveIntegerField(default=0,null=True )
    pointsToLose = models.PositiveIntegerField(default=0, null=True)
    availability = models.JSONField(default=dict)

    def __str__(self):
        return self.user.username

       
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def get_personal_competences(self):
        return self.competences.filter(type=CompetenceType.PERSONAL)

    def update_points_after_invitation(self, points_to_win: int, points_to_lose: int, is_sender: bool):
        """
        Met à jour les points du joueur et prépare les points à gagner/perdre
        après l'acceptation d'une invitation.
        """
        if is_sender:
            # Le sender perd immédiatement des points du receiver
            self.points = max(0, self.points - points_to_lose)

        self.pointsToWin = points_to_win
        self.pointsToLose = points_to_lose
        self.save(update_fields=["points", "pointsToWin", "pointsToLose"])
    
