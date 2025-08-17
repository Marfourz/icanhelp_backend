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
        depth = 2
        model = UserProfil
        fields = '__all__'
        ordering = ['id']
    
    def update(self, instance, validated_data):
        # Récupération des données utilisateur imbriquées
        user_data = validated_data.pop('user', {})
        username = user_data.get('username')

        # Met à jour le user.username si fourni
        if username:
            instance.user.username = username
            instance.user.save()

        # Met à jour les autres champs du profil
        return super().update(instance, validated_data)


class MyProfilSerializer(serializers.ModelSerializer):

    nb_skill_learn_finished = serializers.SerializerMethodField()
    nb_skill_learn_started = serializers.SerializerMethodField()

    user = UserSerializer()
    
    class Meta:
        depth = 2
        model = UserProfil
        fields = '__all__'
        ordering = ['id']
    
    def get_nb_skill_learn_started(self, obj):
        return obj.sendInvitations.exclude(state="PENDING").count()

    def get_nb_skill_learn_finished(self, obj):
        return obj.sendInvitations.filter(state="VALIDATED").count()
    

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

class InvitationSerializer(serializers.ModelSerializer):
    discussion = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        depth = 3
        model = Invitation
        fields = '__all__'
        ordering = ['-createdAt']

class CreateInvitationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Invitation
        fields = ['id', 'receiver', 'createdBy', 'sender_competence', 'receiver_competence', 'senderPoints', 'receiverPoints', 'duration', 'message', 'discussion']
  

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id','message','sender', 'type', 'createdAt']

class UserCompetenceCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False)  # optionnel

    class Meta:
        depth = 2
        model = UserCompetence
        fields = ['id','description', 'points','duration', 'level', 'title', 'category_id', 'type', 'category', 'user']

        read_only_fields = ['category', 'user']

    def create(self, validated_data, user_profil):
        category_id = validated_data.pop('category_id', None)

        if not category_id:
            raise serializers.ValidationError("Catégorie nécessaire.")

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Catégorie introuvable.")
        
        return UserCompetence.objects.create(
            category=category,
            user=user_profil,
            **validated_data
        )

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'

