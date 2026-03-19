from django.db import models

from api.utils.upload_paths import get_upload_category_path

class Category(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    icon_name = models.CharField(max_length=100, help_text="Nom de l’icône Flutter (ex: 'sports_soccer')")
    color = models.CharField(max_length=7, default="#cccccc")
    image = models.FileField(upload_to = get_upload_category_path, blank=True, null=True,default=None)


    def __str__(self):
        return self.name
    
    class Meta:
       verbose_name_plural = "Categories"