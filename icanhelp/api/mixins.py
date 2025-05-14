from api.models import UserProfil

class UserProfilMixin:
    """Mixin permettant d'injecter le UserProfil dans toutes les vues"""

    def get_user_profil(self):
        """Récupérer le UserProfil lié à l'utilisateur connecté"""
        return UserProfil.objects.get(user=self.request.user)