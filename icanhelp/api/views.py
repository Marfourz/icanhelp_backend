from django.shortcuts import render

from api.models import *
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from api.serializers import GroupSerializer, UserSerializer, CompetenceSerializer

from rest_framework.response import Response
from api.serializers import UserProfilSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserProfilViewSet(viewsets.ModelViewSet):
    queryset = UserProfil.objects.all()
    serializer_class = UserProfilSerializer

    @action(detail=True, methods=['post'])
    def ajouter_competences_voulues(self, request, pk=None):
        user = self.get_object()
        competence_ids = request.data.get('competence_ids', []) 
        competences = Competence.objects.filter(id__in=competence_ids)

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=400)
        competences = Competence.objects.filter(id__in=competence_ids)

        if not competences.exists():
            return Response({"error": "Aucune compétence valide trouvée."}, status=400)

        user.competences_desired.add(*competences)
        return Response({"message": "Compétences ajoutées aux compétences voulues", "competences": [c.title for c in competences]})

    @action(detail=True, methods=['post'])
    def ajouter_competences_personnelles(self, request, pk=None):
        user = self.get_object()
        competence_ids = request.data.get('competence_ids', []) 
        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=400)
        competences = Competence.objects.filter(id__in=competence_ids)

        if not competences.exists():
            return Response({"error": "Aucune compétence valide trouvée."}, status=400)

        user.competences_persornal.add(*competences)
        return Response({"message": "Compétences ajoutées aux compétences personnelles", "competences": [c.title for c in competences]})
    


    @action(detail=True, methods=['delete'])
    def supprimer_competences_voulues(self, request, pk=None):
        """Supprime des compétences des compétences voulues d'un utilisateur."""
        user = self.get_object()
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=400)

        competences = user.competences_desired.filter(id__in=competence_ids)

        if not competences.exists():
            return Response({"error": "Aucune compétence trouvée dans les compétences voulues."}, status=400)

        user.competences_desired.remove(*competences)
        return Response({
            "message": "Compétences supprimées des compétences voulues.",
            "competences": [c.title for c in competences]
        }, status=200)
    

    @action(detail=True, methods=['delete'])
    def supprimer_competences_personnelles(self, request, pk=None):
        """Supprime des compétences des compétences personnelles d'un utilisateur."""
        user = self.get_object()
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=400)

        competences = user.competences_persornal.filter(id__in=competence_ids)

        if not competences.exists():
            return Response({"error": "Aucune compétence trouvée dans les compétences personnelles."}, status=400)

        user.competences_persornal.remove(*competences)
        return Response({
            "message": "Compétences supprimées des compétences personnelles.",
            "competences": [c.title for c in competences]
        }, status=200)



class UserProfilViewSet(viewsets.ModelViewSet):
    queryset = UserProfil.objects.all()
    serializer_class = UserProfilSerializer


class UserCompetenceVoulueViewSet(viewsets.ViewSet):
    """
    Gère les compétences voulues d'un utilisateur :
    - GET : Récupère les compétences voulues
    - POST : Ajoute des compétences
    - DELETE : Supprime des compétences
    """

    def list(self, request, userprofil_pk=None):
        """Récupérer les compétences voulues"""
        user_profil = get_object_or_404(UserProfil, pk=userprofil_pk)
        competences = user_profil.competences_desired.all()
        return Response({"competences": [c.nom for c in competences]})

    def create(self, request, userprofil_pk=None):
        """Ajouter des compétences voulues"""
        user_profil = get_object_or_404(UserProfil, pk=userprofil_pk)
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

        competences = Competence.objects.filter(id__in=competence_ids)
        user_profil.competences_desired.add(*competences)

        return Response({
            "message": "Compétences ajoutées.",
            "competences": [c.nom for c in competences]
        })

    def destroy(self, request, userprofil_pk=None):
        """Supprimer des compétences voulues"""
        user_profil = get_object_or_404(UserProfil, pk=userprofil_pk)
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

        competences = user_profil.competences_desired.filter(id__in=competence_ids)
        if not competences.exists():
            return Response({"error": "Aucune compétence trouvée."}, status=status.HTTP_400_BAD_REQUEST)

        user_profil.competences_desired.remove(*competences)
        return Response({
            "message": "Compétences supprimées.",
            "competences": [c.nom for c in competences]
        })


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CompetenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Competence.objects.all().order_by('created')
    serializer_class = CompetenceSerializer
    permission_classes = []


# class DiscussionViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Discussion.objects.all().order_by('name')
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]



