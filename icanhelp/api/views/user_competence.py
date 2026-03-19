from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import UserCompetence, Category
from api.serializers import UserCompetenceCreateSerializer
from api.mixins import UserProfilMixin
from api.models.UserCompetence import CompetenceType
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

DEFAULT_POINTS_PER_HOUR = 1

class UserCompetencesAPIView(UserProfilMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def get(self, request):
        type = request.query_params.get('type')
        user_profil = self.get_user_profil()

        queryset = UserCompetence.objects.filter(user=user_profil)

        if type in [CompetenceType.DESIRED, CompetenceType.PERSONAL]:
            queryset = queryset.filter(type=type)

        serializer = UserCompetenceCreateSerializer(queryset.order_by('-createdAt'), many=True,context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCompetenceCreateSerializer(
            data=request.data,
            context={'request': request} )
        if serializer.is_valid():
            user_profil = self.get_user_profil()
            competence = serializer.create(serializer.validated_data, user_profil=user_profil)
            return Response(UserCompetenceCreateSerializer(competence).data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        user_profil = self.get_user_profil()
        competence_ids = [id]

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

        competences = UserCompetence.objects.filter(id__in=competence_ids, user=user_profil)
        deleted_ids = list(competences.values_list('id', flat=True))

        if not deleted_ids:
            return Response({"error": "Aucune compétence trouvée."}, status=status.HTTP_404_NOT_FOUND)

        competences.delete()

        return Response({
            "message": "Compétences supprimées.",
            "competences": deleted_ids
        })

    def put(self, request, id):
        user_profil = self.get_user_profil()

        try:
            competence = UserCompetence.objects.get(id=id, user=user_profil)
        except UserCompetence.DoesNotExist:
            return Response({"error": "Compétence non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserCompetenceCreateSerializer(competence, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Compétence mise à jour.",
                "competence": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CompetenceDefaultPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        category_id = request.query_params.get('category')
        type = request.query_params.get('type')

        if type not in [CompetenceType.DESIRED, CompetenceType.PERSONAL]:
            return Response({"error": "Type de compétence non trouvé."}, status=400)

        category = get_object_or_404(Category, id=category_id)

        competences = UserCompetence.objects.filter(
            type=type,
            category=category,
            points__isnull=False,
            duration__isnull=False,
            duration__gt=0
        )

        if not competences.exists():
            return Response({
                "points_per_hour": DEFAULT_POINTS_PER_HOUR,
                "based_on": 0,
            })

        taux_list = sorted([float(c.points / c.duration) for c in competences])

        q1 = taux_list[len(taux_list) // 4]
        q3 = taux_list[(3 * len(taux_list)) // 4]
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        filtered = [t for t in taux_list if lower <= t <= upper]

        if not filtered:
            return Response({
                "points_per_hour": DEFAULT_POINTS_PER_HOUR,
                "based_on": 0,
            })

        taux_moyen = round(sum(filtered) / len(filtered), 2)

        return Response({
            "points_per_hour": taux_moyen,
            "based_on": len(filtered),
        })