from api.models.UserProfil import UserProfil
from api.serializers import UserProfilSerializer, UserSerializer
from django.contrib.auth.models import User
from api.mixins import UserProfilMixin

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
        if not search_text:
            return Response({"error": "Search text is required"}, status=400)

        competences = Competence.objects.prefetch_related('user_personal').all()

        for user in UserProfil.objects.all():
            print(user.competences_persornal.all())

        match_profils = [
            user_personal for competence in competences
            for user_personal in competence.user_personal.all()
            if predict_match(search_text, competence.title) > LIMIT_TO_MATCH
        ]

        serializer = UserProfilSerializer(match_profils, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='search')
    def search2(self, request):
        query = request.GET.get('search')
        if not query:
            return Response({"error": "Search text is required"}, status=400)

        query_embedding = model.encode(query, convert_to_tensor=True)

        results = []

        for user in UserProfil.objects.prefetch_related('competences_persornal').all():
            comp_texts = [comp.nom for comp in user.competences_persornal.all()]
            if not comp_texts:
                continue

            comp_embeddings = model.encode(comp_texts, convert_to_tensor=True)
            similarities = util.cos_sim(query_embedding, comp_embeddings)[0]

            # Similarity moyenne comme score global
            avg_score = float(torch.mean(similarities))

            # Compétences matchées au-dessus d’un seuil
            matched = [
                {"competence": comp, "score": float(sim)}
                for comp, sim in zip(comp_texts, similarities)
                if sim > 0.5  # seuil à ajuster
            ]

            results.append({
                "user": user.id,
                "match_score": round(avg_score, 3),
                "matched_competences": matched
            })

        results.sort(key=lambda x: x["match_score"], reverse=True)

        return Response(results)

