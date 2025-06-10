from django.db import models
from api.models import Category


class Competence(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True)

    
    class Meta:
        ordering = ['created']


        