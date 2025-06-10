from api.models import *
from api.serializers import CompetenceSerializer 

from rest_framework import permissions,status,viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from api.mixins import UserProfilMixin


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

    
