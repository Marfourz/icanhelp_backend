from django.contrib.auth.models import User
from django.db import models
from api.utils.upload_paths import get_upload_path

from api.models.UserCompetence import CompetenceType
from api.models.Invitation import InvitationType


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
    avatar = models.FileField(upload_to= get_upload_path, blank=True, null=True,default=None)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def get_personal_competences(self):
        return self.competences.filter(type=CompetenceType.PERSONAL)
    
    def get_categories(self, type=None):
        qs = self.competences.all()

        if type == CompetenceType.DESIRED:
            qs = qs.filter(type=CompetenceType.DESIRED)
        elif type == CompetenceType.PERSONAL:
            qs = qs.filter(type=CompetenceType.PERSONAL)    

        return qs.values_list("categorie", flat=True).distinct()


    def accept_invitation(self, invitation):
        """Met les points en attente selon le rôle et le type."""
        is_sender = self == invitation.createdBy

        if invitation.type == InvitationType.LEARN:
            if is_sender:
                self.pointsToLose += invitation.points  # sender va dépenser
            else:
                self.pointsToWin += invitation.points   # receiver va gagner
        else:  # TEACH
            if is_sender:
                self.pointsToWin += invitation.points   # sender va gagner
            else:
                self.pointsToLose += invitation.points  # receiver va dépenser

        self.save(update_fields=["pointsToWin", "pointsToLose"])


    def validate_invitation(self, invitation):
        """Transfère les points définitivement."""
        is_sender = self == invitation.createdBy

        if invitation.type == InvitationType.LEARN:
            if is_sender:
                self.pointsToLose = max(0, self.pointsToLose - invitation.points)
                self.points = max(0, self.points - invitation.points)  # sender perd
            else:
                self.pointsToWin = max(0, self.pointsToWin - invitation.points)
                self.points += invitation.points  # receiver gagne
        else:  # TEACH
            if is_sender:
                self.pointsToWin = max(0, self.pointsToWin - invitation.points)
                self.points += invitation.points  # sender gagne
            else:
                self.pointsToLose = max(0, self.pointsToLose - invitation.points)
                self.points = max(0, self.points - invitation.points)  # receiver perd

        self.save(update_fields=["points", "pointsToWin", "pointsToLose"])


    def reject_invitation(self, invitation):
        """Annule les points en attente."""
        is_sender = self == invitation.createdBy

        if invitation.type == InvitationType.LEARN:
            if is_sender:
                self.pointsToLose = max(0, self.pointsToLose - invitation.points)
            else:
                self.pointsToWin = max(0, self.pointsToWin - invitation.points)
        else:  # TEACH
            if is_sender:
                self.pointsToWin = max(0, self.pointsToWin - invitation.points)
            else:
                self.pointsToLose = max(0, self.pointsToLose - invitation.points)

        self.save(update_fields=["pointsToWin", "pointsToLose"])
    def has_enough_points(self, points: int) -> bool:
        return (self.points - self.pointsToLose) >= points
    

## Flux complet
##  LEARN : sender veut apprendre une compétence du receiver
#       → sender dépense `points`, receiver gagne `points`

#TEACH : sender propose d'enseigner au receiver
#       → receiver dépense `points`, sender gagne `points`

#Création  : vérifier has_enough_points() pour le payeur
#ACCEPTED  : points mis en attente (pointsToLose/Win)
#VALIDATED : points transférés définitivement
#REJECTED  : points en attente libérés

