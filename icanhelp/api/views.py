from api.models import *
from api.serializers import GroupSerializer, UserSerializer, CompetenceSerializer,UserProfilSerializer,DiscussionSerializer
from django.contrib.auth.models import Group, User
from api.models.Discussion import DiscussionState

from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count
from rest_framework.decorators import action


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

# Vue API pour l'inscription avec JWT
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Inscription réussie !",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfilViewSet(viewsets.ModelViewSet):
    queryset = UserProfil.objects.all()
    serializer_class = UserProfilSerializer


class UserCompetencesAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,  type = None):
        """Récupérer les compétences voulues"""
        user_id = request.user.id
  
        user_profil = get_object_or_404(UserProfil, pk=user_id)

        if type == "desired":
            competences = user_profil.competences_desired.all()
        else:
            competences = user_profil.competences_persornal.all()

        serializer = CompetenceSerializer(competences, many = True)
        return Response(serializer.data)

    def post(self, request, type=None):
        """Ajouter des compétences voulues"""
        user_profil = get_object_or_404(UserProfil, pk=request.user.id)
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

        competences = Competence.objects.filter(id__in=competence_ids)

        if type == "desired":
            user_profil.competences_desired.add(*competences)
        else:
            user_profil.competences_persornal.add(*competences)

        return Response({
            "message": "Compétences ajoutées.",
            "competences": [c.title for c in competences]
        })

    def delete(self, request, type = None):
        """Supprimer des compétences voulues"""
        user_profil = get_object_or_404(UserProfil, pk=request.user.id)
        competence_ids = request.data.get('competence_ids', [])

        if not competence_ids:
            return Response({"error": "Aucune compétence fournie."}, status=status.HTTP_400_BAD_REQUEST)

        competences = user_profil.competences_desired.filter(id__in=competence_ids)
        if not competences.exists():
            return Response({"error": "Aucune compétence trouvée."}, status=status.HTTP_400_BAD_REQUEST)

        if type == "desired":
            user_profil.competences_desired.remove(*competences)
        else:
            user_profil.competences_persornal.remove(*competences)

  
        return Response({
            "message": "Compétences supprimées.",
            "competences": [c.title for c in competences]
        })
    



class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CompetenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Competence.objects.all().order_by('created')
    serializer_class = CompetenceSerializer
    permission_classes = []

    def get_queryset(self):

        type = self.request.GET.get('type')
        limit = self.request.GET.get('limit')

        if limit:
            limit =  int(self.request.GET.get('limit')) 
        
        if type is None:
            query = Competence.objects.all()
        else:
            if type == 'desired':
                query = Competence.objects.filter(user_desired__isnull=False).annotate(
                    total = Count("user_desired")
                ).order_by("-total").distinct()[:limit]
            else:
                query = Competence.objects.filter(user_personal__isnull=False).annotate(
                    total = Count("user_personal")
                ).order_by("-total").distinct()[:limit]

        return query
    


class InvitationViewSet(viewsets.ModelViewSet):

    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]


    
    @action(detail=True, methods = ['post'])     
    def accept(self, request, pk = None):
        
        # discussion_id = request.data.get("discussion_id")
        discussion = get_object_or_404(Discussion, pk=pk)

        print(discussion.receiver, request.user)
        if discussion.receiver.id != request.user.id:
              return Response({"message": "Vous n'êtes pas autorisé à accepter cette invitation."}, status=status.HTTP_403_FORBIDDEN)
        
        discussion.state = DiscussionState.ACCEPTED
        
        discussion.save()
        serializer = DiscussionSerializer(discussion, many =False, context={'request': request})

        return Response(serializer.data)
    
    @action(detail=True, methods = ['post'])     
    def reject(self, request, pk = None):
        
        # discussion_id = request.data.get("discussion_id")
        discussion = get_object_or_404(Discussion, pk=pk)

        if discussion.receiver.id != request.user.id:
              return Response({"message": "Vous n'êtes pas autorisé à rejeter cette invitation."}, status=status.HTTP_403_FORBIDDEN)
        discussion.state = DiscussionState.REJECTED
        
        discussion.save()
        serializer = DiscussionSerializer(discussion, many =False, context={'request': request})

        return Response(serializer.data)

   
    def get_queryset(self):
        user = self.request.user.id 
        type = self.request.GET.get("type")

        invitations = Discussion.objects.filter(state = DiscussionState.PENDING)

        if type == "send":
            invitations = invitations.filter(createdBy = user)
        elif type == "receive":
            invitations = invitations.filter(receiver = user)
        

        return invitations
    
    def post(self, request):
       
         receiver_id = request.data.get("receiver_id")
         receiver = get_object_or_404(UserProfil, pk=receiver_id)
         sender = get_object_or_404(UserProfil, pk=request.user.id)
         discussion = Discussion()
         discussion.receiver = receiver
         discussion.createdBy = sender
         
         return Response(discussion.save())


         

        


# class DiscussionViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Discussion.objects.all().order_by('name')
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]



