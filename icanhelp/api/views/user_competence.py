from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import UserCompetence, Category
from api.serializers import UserCompetenceCreateSerializer
from api.mixins import UserProfilMixin
from api.models.UserCompetence import CompetenceType
from api.utils.errors import ErrorCode, api_error, validation_error
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

DEFAULT_POINTS_PER_HOUR = 1


class UserCompetencesAPIView(UserProfilMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def get(self, request):
        comp_type = request.query_params.get('type')
        user_profil = self.get_user_profil()

        queryset = UserCompetence.objects.filter(user=user_profil)
        if comp_type in [CompetenceType.DESIRED, CompetenceType.PERSONAL]:
            queryset = queryset.filter(type=comp_type)

        serializer = UserCompetenceCreateSerializer(
            queryset.order_by('-createdAt'), many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCompetenceCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        user_profil = self.get_user_profil()
        competence = serializer.create(serializer.validated_data, user_profil=user_profil)
        return Response(UserCompetenceCreateSerializer(competence).data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user_profil = self.get_user_profil()
        competence = UserCompetence.objects.filter(id=id, user=user_profil).first()

        if not competence:
            return api_error(ErrorCode.COMPETENCE_NOT_FOUND, "Compétence introuvable.", status=status.HTTP_404_NOT_FOUND)

        competence.delete()
        return Response({"message": "Compétence supprimée.", "id": id})

    def put(self, request, id):
        user_profil = self.get_user_profil()
        competence = UserCompetence.objects.filter(id=id, user=user_profil).first()

        if not competence:
            return api_error(ErrorCode.COMPETENCE_NOT_FOUND, "Compétence introuvable.", status=status.HTTP_404_NOT_FOUND)

        serializer = UserCompetenceCreateSerializer(
            competence, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return Response({"message": "Compétence mise à jour.", "competence": serializer.data})


class CompetenceDefaultPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        category_id = request.query_params.get('category')
        comp_type = request.query_params.get('type')

        if comp_type not in [CompetenceType.DESIRED, CompetenceType.PERSONAL]:
            return api_error(ErrorCode.COMPETENCE_TYPE_INVALID, "Type de compétence invalide. Valeurs acceptées : personal, desired.")

        category = get_object_or_404(Category, id=category_id)

        competences = UserCompetence.objects.filter(
            type=comp_type,
            category=category,
            points__isnull=False,
            duration__isnull=False,
            duration__gt=0,
        )

        if not competences.exists():
            return Response({"points_per_hour": DEFAULT_POINTS_PER_HOUR, "based_on": 0})

        taux_list = sorted([float(c.points / c.duration) for c in competences])

        q1 = taux_list[len(taux_list) // 4]
        q3 = taux_list[(3 * len(taux_list)) // 4]
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        filtered = [t for t in taux_list if lower <= t <= upper] or taux_list

        return Response({
            "points_per_hour": round(sum(filtered) / len(filtered), 2),
            "based_on": len(filtered),
        })
