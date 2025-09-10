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
from django.db.models import Q, F
from django.db.models import Case, When, Value, IntegerField, FloatField
from django.db.models.expressions import RawSQL
from django.db.models.functions import ACos, Cos, Radians, Sin, Coalesce



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
        user_profil = self.get_user_profil()
        q = request.query_params.get('q', '')
        category_id = request.query_params.get('category_id', None)
        type = request.query_params.get('type', None)

        # 🔎 Catégories de l'utilisateur
        my_categories = list(user_profil.competences.values_list("category_id", flat=True))

        # Base queryset : exclure mes propres compétences
        queryset = UserCompetence.objects.exclude(user=user_profil)

        # Filtre commun
        filters = Q()
        if type:
            filters &= Q(type=type)
        if q:
            filters &= Q(title__icontains=q) | Q(description__icontains=q)
        if category_id:
            filters &= Q(category_id=category_id)

        queryset = queryset.filter(filters)

        # Priorité : mes catégories d'abord
        queryset = queryset.annotate(
            in_my_categories=Case(
                When(category_id__in=my_categories, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )

        # Distance si lat/lon renseignées
        if user_profil.location_lat and user_profil.location_lon:
            
            queryset = queryset.annotate(
                distance=6371 * ACos(
                    Cos(Radians(user_profil.location_lat)) *
                    Cos(Radians(Coalesce(F('user__location_lat'), Value(0.0, output_field=FloatField())))) *
                    Cos(Radians(Coalesce(F('user__location_lon'), Value(0.0, output_field=FloatField()))) - Radians(user_profil.location_lon)) +
                    Sin(Radians(user_profil.location_lat)) *
                    Sin(Radians(Coalesce(F('user__location_lat'), Value(0.0, output_field=FloatField()))))
                )
            )
            # Tri : mes catégories par distance, puis les autres par distance
            queryset = queryset.order_by(
                '-in_my_categories',
                Case(
                    When(in_my_categories=1, then=F('distance')),
                    default=F('distance')
                )
            )
        else:
            queryset = queryset.order_by('-in_my_categories')
        
        for competence in queryset[:15]:  # juste les 10 premiers pour tester
            print(f"{competence.title} - Distance: {getattr(competence, 'distance', 'N/A')} km")

        # Pagination native
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)