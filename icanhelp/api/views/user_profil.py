from api.models.UserProfil import UserProfil
from api.serializers import UserProfilSerializer, UserSerializer
from django.contrib.auth.models import User
from api.mixins import UserProfilMixin
from api.models import Competence
from api.serializers import CompetenceSerializer

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from model.matching import predict_match


LIMIT_TO_MATCH = 0.7

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]



class UserProfilViewSet(UserProfilMixin, viewsets.ModelViewSet):
    queryset = UserProfil.objects.all()
    serializer_class = UserProfilSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        userProfil = self.get_user_profil()
        return UserProfil.objects.exclude(id = userProfil.id)
    
    @action(detail=False, methods=['get'], url_path='my_profil')
    def my_profil(self, request):
        user_profile = UserProfil.objects.get(user=request.user)
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        search_text = request.GET.get('search')
        competences = Competence.objects.all()
        matching_competences = []
        match_profils = []
        for competence in competences:
            taux_match = predict_match(search_text, competence.title)
            print(search_text , ' ', competence.title, ' : ', taux_match)
            if taux_match > LIMIT_TO_MATCH:
                matching_competences.append(competence.title)
                print(competence.user_personal, "user personal")
                match_profils.extend(competence.user_personal.all())
            serialier = UserProfilSerializer(match_profils, many=True)

        print("Total matching : ", matching_competences)
        return Response(serialier.data)
