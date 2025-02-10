from django.contrib.auth.models import User
from django.db import models
from api.models.Competence import Competence



class UserProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")

    competences_desired = models.ManyToManyField(
        Competence, blank=True, related_name="user_desired"
    )
    competences_persornal = models.ManyToManyField(
        Competence,  blank=True, related_name="user_personal"
    )

    def __str__(self):
        return self.user.username
    
