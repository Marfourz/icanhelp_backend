from rest_framework import viewsets, permissions
from api.models import UserCompetence
from api.serializers import UserCompetenceCreateSerializer
from api.mixins import UserProfilMixin
from rest_framework.views import APIView
from rest_framework.views import Response,status


class UserCompetencesAPIView(UserProfilMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserCompetenceCreateSerializer

    def get(self, request,  type = None):
        """Récupérer les compétences voulues"""

        user_profil = self.get_user_profil()

        if type == "desired":
            competences = user_profil.competences_desired.all()
        else:
            competences = user_profil.competences_persornal.all()

        serializer = UserCompetenceCreateSerializer(competences, many = True)
        return Response(serializer.data)
    
    def post(self, request, type=None):
        user_profil = self.get_user_profil()
        serializer = UserCompetenceCreateSerializer(data=request.data)
        if serializer.is_valid():
            
            competence = serializer.save()

            if type == "desired":
                user_profil.competences_desired.add(competence)
            else:
                user_profil.competences_persornal.add(competence)

            user_profil.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
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
            "competences": [c.id for c in competences]
        })
    

    def put(self, request, type, id):
        """Met à jour une compétence liée au profil utilisateur"""
        user_profil = self.get_user_profil()

        if type == "desired":
            queryset = user_profil.competences_desired  
        else:
            queryset = user_profil.competences_persornal 

        try:
            user_competence = queryset.get(id=id)
        except UserCompetence.DoesNotExist:
            return Response({"error": "Compétence non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserCompetenceCreateSerializer(user_competence, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Compétence mise à jour.",
                "competence": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        