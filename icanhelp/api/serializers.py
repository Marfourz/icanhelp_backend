from django.contrib.auth.models import Group, User
from api.models import Invitation,Category
from api.models import InvitationState
from rest_framework import serializers
from django.db import transaction
from api.models import *
from PIL import Image
import os

class ImageUploadSerializer(serializers.ModelSerializer):

    def get_image_url(self, obj, field_name):
        image = getattr(obj, field_name, None)
        if not image:
            return None

        url = image.url
        minio_internal = os.getenv("MINIO_INTERNAL_URL", "http://minio:9000")
        minio_external = os.getenv("MINIO_EXTERNAL_URL", "http://localhost:9000")

        return url.replace(minio_internal, minio_external)

    def update_image(self, instance, validated_data, field_name):
        old_image = getattr(instance, field_name).name if getattr(instance, field_name) else None
        new_image = validated_data.get(field_name)

        setattr(instance, field_name, new_image)

        if old_image and old_image != new_image.name:
            getattr(instance, field_name).storage.delete(old_image)

        instance.save()
        return instance

    def save_image_from_upload(self, instance, field_name, upload):
        """
        Sauvegarde un fichier uploadé dans le champ field_name.
        Supprime l'ancienne image si elle existe.
        """
        current = getattr(instance, field_name)

        # Supprimer l'ancienne image
        if current:
            current.storage.delete(current.name)

        # Sauvegarder la nouvelle
        getattr(instance, field_name).save(upload.name, upload, save=True)

    @staticmethod
    def validate_image_file(value):
        if not value:
            return
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Fichier trop volumineux (max 2MB).")

        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Format non autorisé.")

        try:
            image = Image.open(value)
            image.load()
        except Exception:
            raise serializers.ValidationError("Fichier image invalide.")
        value.seek(0)
        return value
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']

class UserPulicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserProfilSerializer(ImageUploadSerializer):

    user = UserPulicSerializer()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfil
        fields = ['id', 'user', 'bio', 'city', 'adress', 'points', 'avatar']
        ordering = ['id']

    
    def update(self, instance, validated_data):
        # Récupération des données utilisateur imbriquées
        user_data = validated_data.pop('user', {})
        with transaction.atomic():
            username = user_data.get('username')

            # Met à jour le user.username si fourni
            if username:
                instance.user.username = username
                instance.user.save()
        instance = super().update(instance, validated_data)

        # Met à jour les autres champs du profil
        return instance
    
    def get_avatar(self, obj):
        return self.get_image_url(obj, 'avatar')


class AvatarSerializer(ImageUploadSerializer):

    class Meta:
        model = UserProfil
        fields = ['avatar']

    def update(self, instance, validated_data):
        return self.update_image(instance, validated_data, 'avatar')
    
    def validate_avatar(self, value):
        return self.validate_image_file(value)
        
class MyProfilSerializer(ImageUploadSerializer):

    avatar = serializers.SerializerMethodField()
    nb_skill_learn_finished = serializers.SerializerMethodField()
    nb_skill_learn_started = serializers.SerializerMethodField()
    competences = serializers.SerializerMethodField()

    user = UserSerializer()
    
    class Meta:
        depth = 2
        model = UserProfil
        fields = '__all__'
        ordering = ['id']
    
    def get_nb_skill_learn_started(self, obj):
        return obj.sendInvitations.exclude(state="PENDING").count()

    def get_nb_skill_learn_finished(self, obj):
        return obj.sendInvitations.filter(state=InvitationState.VALIDATED).count()
    
    def get_avatar(self, obj):
       return self.get_image_url(obj,'avatar')
    
    def get_competences(self, obj):
        competences = obj.competences.all()

        return UserCompetenceCreateSerializer(
            competences,
            many=True,
            context=self.context
        ).data
    

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

    createdBy = UserProfilSerializer()
    class Meta:
        depth = 3
        model = Invitation
        fields = '__all__'
        ordering = ['-createdAt']

class CreateInvitationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Invitation
        fields = ['id', 'receiver', 'createdBy', 'competence','points', 'duration', 'message', 'discussion', 'type']


class CategorySerializer(ImageUploadSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_image(self, obj):
        return self.get_image_url(obj, 'image')

    def validate_image(self, value):
        return self.validate_image_file(value)

    def update(self, instance, validated_data):
        return self.update_image(instance, validated_data, 'image')
  

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id','message','sender', 'type', 'createdAt']



class UserCompetenceCreateSerializer(ImageUploadSerializer):
    category_id = serializers.IntegerField(write_only=True, required=True)
    image = serializers.SerializerMethodField()
    image_upload = serializers.ImageField(write_only=True, required=False)
    user = UserProfilSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = UserCompetence
        fields = ['id', 'description', 'points', 'duration', 'level', 'title',
                  'category_id', 'type', 'category', 'user', 'image', 'image_upload']
        read_only_fields = ['category', 'user']

    def get_image(self, obj):
        return self.get_image_url(obj, 'image')

    def validate_image_upload(self, value):
        return self.validate_image_file(value)

    def create(self, validated_data, user_profil):
        category_id = validated_data.pop('category_id')
        image_upload = validated_data.pop('image_upload', None)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Catégorie introuvable.")

        instance = UserCompetence.objects.create(
            category=category,
            user=user_profil,
            **validated_data
        )

        if image_upload:
            self.save_image_from_upload(instance, 'image', image_upload)

        return instance

    def update(self, instance, validated_data):
        image_upload = validated_data.pop('image_upload', None)

        for field in ['description', 'points', 'duration', 'level', 'title', 'type', 'category_id']:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))

        if image_upload:
            self.save_image_from_upload(instance, 'image', image_upload)
        else:
            instance.save()

        return instance