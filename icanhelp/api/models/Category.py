from django.db import models

class Category(models.Model):
    
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    icon_name = models.CharField(max_length=100, help_text="Nom de l’icône Flutter (ex: 'sports_soccer')")
    color = models.CharField(max_length=7, default="#cccccc")


    def __str__(self):
        return self.name
    
    class Meta:
       verbose_name_plural = "Categories"