from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from api.models import UserProfil

@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    """Créer automatiquement un UserProfil quand un User est créé."""
    if created:  # Vérifie si c'est une nouvelle création
        UserProfil.objects.create(user=instance)
