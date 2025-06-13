
from django.db import models

from api.models import Category

class UserCompetence(models.Model):

    title = models.CharField(max_length=100, blank=True, default='')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True)
    description = models.TextField(blank=True, null=True)
    points_per_hour = models.PositiveIntegerField(blank=True, null=True)
    level = models.CharField(max_length=50, choices=[('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé')],  blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
    
    class Meta:
        ordering = ['createdAt']
