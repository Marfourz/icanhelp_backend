from api.models import *

from rest_framework import permissions,status,viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from api.mixins import UserProfilMixin
from api.serializers import UserCompetenceCreateSerializer
from django.db.models import Count
from rest_framework.decorators import action
from api.models import Category
from api.models.UserCompetence import CompetenceType
from django.db.models import Q



class CompetenceViewSet(UserProfilMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserCompetence.objects.all()
    serializer_class = UserCompetenceCreateSerializer
    
    def get_queryset(self):
        """
            Récupère les compétences les plus recherchées, c'est-à-dire celles de type "desired",
            triées par le nombre de personnes qui les ont en competences_desired.
        """
        limit = self.request.query_params.get('limit', None)
        competence_type = self.request.query_params.get('type', None)

        queryset = UserCompetence.objects.all()

        if competence_type == "desired":
            # Annoter avec combien de UserProfil désirent cette compétence
            queryset = queryset.filter(type=CompetenceType.DESIRED)

        elif competence_type == "personal":
            queryset = queryset.filter(type=CompetenceType.PERSONAL)

        # Appliquer la limite éventuelle
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass  # Ignore mauvaise valeur

        return queryset
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Recherche des compétences filtrées par texte libre (titre ou description)
        et/ou catégorie.
        - ?q=python
        - ?category=3
        - ?q=python&category=5
        """

        user_profil = self.get_user_profil()
        q = request.query_params.get('q', '')
        category_id = request.query_params.get('category_id', None)
        type = request.query_params.get('type', None)

        queryset = UserCompetence.objects.exclude(user=user_profil)

        if type:
             queryset = queryset.filter(
                type=type
            )

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # ✅ Appliquer la pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback si pagination désactivée
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)