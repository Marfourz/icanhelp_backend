from api.models import *
from api.serializers import CompetenceSerializer 

from rest_framework import permissions,status,viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from api.mixins import UserProfilMixin

class UserCompetencesAPIView(UserProfilMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,  type = None):
        """Récupérer les compétences voulues"""
  
        user_profil = self.get_user_profil()

        if type == "desired":
            competences = user_profil.competences_desired.all()
        else:
            competences = user_profil.competences_persornal.all()

        serializer = CompetenceSerializer(competences, many = True)
        return Response(serializer.data)
    def post(self, request, type=None):
            """Ajouter des compétences voulues à partir d'une liste de chaînes"""
            user_profil = self.get_user_profil()
            competence_names = request.data.get('competences', [])

            if not competence_names:
                return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

            competences = []
            for name in competence_names:
                competence, created = Competence.objects.get_or_create(title=name)
                competences.append(competence)

            if type == "desired":
                user_profil.competences_desired.add(*competences)
                serializer = CompetenceSerializer( user_profil.competences_desired, many = True)
            else:
                user_profil.competences_persornal.add(*competences)
                serializer = CompetenceSerializer( user_profil.competences_persornal, many = True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, type = None):
        """Supprimer des compétences voulues"""
        user_profil = self.get_user_profil()
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)
        
        if type == "desired":
            competences = user_profil.competences_desired.filter(id__in=competence_ids)
        else:
            competences = user_profil.competences_persornal.filter(id__in=competence_ids)

        
        if not competences.exists():
            return Response({"error": "Aucune compétence trouvée."}, status=status.HTTP_400_BAD_REQUEST)

        if type == "desired":
            user_profil.competences_desired.remove(*competences)
        else:
            user_profil.competences_persornal.remove(*competences)

  
        return Response({
            "message": "Compétences supprimées.",
            "competences": [c.title for c in competences]
        })
    




class CompetenceViewSet(UserProfilMixin, viewsets.ModelViewSet):
    serializer_class = CompetenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Competence.objects.all()

    def get_queryset(self):
        """
        Récupère la liste des compétences en fonction des filtres.
        - ?limit=2 : Limite le nombre de résultats
        - ?type=desired : Filtre par compétences souhaitées
        - ?type=personal : Filtre par compétences personnelles
        """
        queryset = Competence.objects.all()
        limit = self.request.query_params.get('limit', None)
        competence_type = self.request.query_params.get('type', None)

        if competence_type and competence_type in ["desired", "personal"]:
            user_profil = self.get_user_profil()

            if competence_type == "desired":
                queryset = queryset.filter(invitation_competences_desired__receiver=user_profil)
            elif competence_type == "personal":
                queryset = queryset.filter(invitation_competences_personal__createdBy=user_profil)

        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass 

        return queryset

    
