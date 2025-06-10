from django.contrib.auth.models import Group, User
from api.models import Invitation,Category
from rest_framework import serializers
from api.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserProfilSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    
    class Meta:
        depth = 1
        model = UserProfil
        fields = '__all__'
        ordering = ['id']

class UserProfilSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    
    class Meta:
        depth = 1
        model = UserProfil
        fields = '__all__'
        ordering = ['id']


class DiscussionSerializer(serializers.ModelSerializer):
    lastMessage = serializers.SerializerMethodField()
    lastOpenAt = serializers.DateTimeField(read_only=True)
    nbMessagesNotRead = serializers.IntegerField(read_only=True)

    class Meta:
        depth = 2
        model = Discussion
        fields = '__all__'

    def get_lastMessage(self, obj):
        if obj.lastMessage:
            return {
                "content": obj.lastMessage.message,
                "sender": obj.lastMessage.sender.id,
                "created_at": obj.lastMessage.createdAt
            }
        return None

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = ['id', 'title']


class InvitationSerializer(serializers.ModelSerializer):
    
    class Meta:
        depth = 2
        model = Invitation
        fields = ['id', 'receiver', 'createdAt','createdBy', 'competences_desired', 'competences_persornal','state','message']
        ordering = ['-cretedAt']

class CreateInvitationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Invitation
        fields = ['id', 'receiver', 'createdBy', 'competences_desired', 'competences_persornal', 'message']
  

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id','message','sender', 'type', 'createdAt']

class UserCompetenceCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)  # optionnel

    class Meta:
        depth = 2
        model = UserCompetence
        fields = ['description', 'points_per_hour', 'level', 'title', 'category_id', 'competence']

    def create(self, validated_data):
        title = validated_data.pop('title')
        category_id = validated_data.pop('category_id', None)

        category = None
        if category_id:
            from .models import Category
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Catégorie introuvable.")
        else:
            raise serializers.ValidationError("Catégorie necessaire.")

        # Récupérer ou créer la compétence
        competence, _ = Competence.objects.get_or_create(title=title, defaults={'category': category})

        return UserCompetence.objects.create(
            competence=competence,
            **validated_data
        )
    
class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'

