from api.models import UserProfil,Category
from api.serializers import MyProfilSerializer, UserProfilSerializer, UserSerializer
from django.contrib.auth.models import User
from api.mixins import UserProfilMixin

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination


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

    
    # @action(detail=False, methods=['get'], url_path='search')
    # def search(self,request):
    #     userProfil = self.get_user_profil()

    #     if request.GET.get('category_id') :
    #         category = Category.objects.get(id=request.GET.get('category_id'))
    #         categories = [category]
    #         profils = UserProfil.objects.filter(
    #             competences__category__in=categories
    #         ).exclude(id=userProfil.id).distinct()
    #     else:
    #         # 🔹 Étape 1 : récupère les catégories préférées
    #         categories_preferees = userProfil.get_categories()

    #         # 🔸 Étape 2 : profils avec catégories préférées
    #         profils_preferes = UserProfil.objects.filter(
    #             competences__category__in=categories_preferees
    #         ).exclude(id=userProfil.id).distinct()

    #         # 🔸 Étape 3 : profils avec les autres catégories
    #         autres_profils = UserProfil.objects.exclude(
    #             id__in=profils_preferes.values_list('id', flat=True)
    #         ).exclude(id=userProfil.id).distinct()

    #         # 🔹 Étape 4 : fusion avec priorité
    #         profils = list(profils_preferes) + list(autres_profils)

    
    #     search_text = request.GET.get('search')

    #     search_profils = []
    #     if search_text:
    #         scored_profils = []
    #         for profil in profils:
    #             max_score = 0
    #             for competence in profil.competences.all():
    #                 score = predict_match(search_text, competence.title)
    #                 if score > max_score:
    #                     max_score = score
    #             if max_score >= LIMIT_TO_MATCH:
    #                 scored_profils.append((profil, max_score))

    #         # 🔥 Trier par score décroissant
    #         scored_profils.sort(key=lambda x: x[1], reverse=True)

    #         # Extraire uniquement les profils
    #         filtered_profils = [profil for profil, score in scored_profils]
    #     else:
    #         filtered_profils = profils

    #     page = self.paginate_queryset(filtered_profils)

    #     serializer = self.get_serializer(page, many=True)

    #     return self.get_paginated_response(serializer.data)

    
    @action(detail=False, methods=['get'], url_path='my_profil')
    def my_profil(self, request):
        user_profile = UserProfil.objects.get(user=request.user)
        serializer = MyProfilSerializer(user_profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], url_path='my_profil')
    def patch(self, request):
        user_profile = UserProfil.objects.get(user=request.user)
        serializer = UserProfilSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


    # @action(detail=False, methods=['get'], url_path='search')
    # def search(self, request):
    #     search_text = request.GET.get('search')
    #     if not search_text:
    #         return Response({"error": "Search text is required"}, status=400)
    #     competences = Competence.objects.prefetch_related('user_personal').all()

    #     for user in UserProfil.objects.all():
    #         print(user.competences_persornal.all())

    #     match_profils = [
    #         user_personal for competence in competences
    #         for user_personal in competence.user_personal.all()
    #         if predict_match(search_text, competence.title) > LIMIT_TO_MATCH
    #     ]

    #     serializer = UserProfilSerializer(match_profils, many=True)
    #     return Response(serializer.data)
    

    # @action(detail=False, methods=['get'], url_path='search')
    # def search2(self, request):
    #     query = request.GET.get('search')
    #     if not query:
    #         return Response({"error": "Search text is required"}, status=400)

    #     query_embedding = model.encode(query, convert_to_tensor=True)

    #     results = []

    #     for user in UserProfil.objects.prefetch_related('competences_persornal').all():
    #         comp_texts = [comp.nom for comp in user.competences_persornal.all()]
    #         if not comp_texts:
    #             continue

    #         comp_embeddings = model.encode(comp_texts, convert_to_tensor=True)
    #         similarities = util.cos_sim(query_embedding, comp_embeddings)[0]

    #         # Similarity moyenne comme score global
    #         avg_score = float(torch.mean(similarities))

    #         # Compétences matchées au-dessus d’un seuil
    #         matched = [
    #             {"competence": comp, "score": float(sim)}
    #             for comp, sim in zip(comp_texts, similarities)
    #             if sim > 0.5  # seuil à ajuster
    #         ]

    #         results.append({
    #             "user": user.id,
    #             "match_score": round(avg_score, 3),
    #             "matched_competences": matched
    #         })

    #     results.sort(key=lambda x: x["match_score"], reverse=True)

    #     return Response(results)


