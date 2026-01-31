
from django.db import models

class CompetenceType(models.TextChoices):
    PERSONAL = "personal", "Personnelle"
    DESIRED = "desired", "A apprendre"

class UserCompetence(models.Model):

    title = models.CharField(max_length=100, blank=True, default='')
    category = models.ForeignKey('api.Category', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    points = models.PositiveIntegerField(blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True)
    level = models.CharField(max_length=50, choices=[('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé')],  blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey( 'api.UserProfil', related_name="competences", blank=False, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=30,
        choices=CompetenceType.choices, 
        default=CompetenceType.PERSONAL
    )
    #file = models.ImageField(null=True)

    def __str__(self):
        return self.title
