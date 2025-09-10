from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import UserCompetence
from api.serializers import UserCompetenceCreateSerializer
from api.mixins import UserProfilMixin
from api.models.UserCompetence import CompetenceType

class UserCompetencesAPIView(UserProfilMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        type = request.query_params.get('type')
        user_profil = self.get_user_profil()

        queryset = UserCompetence.objects.filter(user=user_profil)

        if type in [CompetenceType.DESIRED, CompetenceType.PERSONAL]:
            queryset = queryset.filter(type=type)

        serializer = UserCompetenceCreateSerializer(queryset.order_by('-createdAt'), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCompetenceCreateSerializer(data=request.data)
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

        serializer = UserCompetenceCreateSerializer(competence, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Compétence mise à jour.",
                "competence": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
