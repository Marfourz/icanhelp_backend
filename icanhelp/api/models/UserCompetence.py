
from django.db import models
from api.models import Competence

class UserCompetence(models.Model):

    description = models.TextField(blank=True, null=True)
    points_per_hour = models.PositiveIntegerField(blank=True, null=True)
    level = models.CharField(max_length=50, choices=[('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé')],  blank=True)
    competence = models.ForeignKey(Competence,  on_delete=models.CASCADE) 
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
    
    class Meta:
        ordering = ['createdAt']
