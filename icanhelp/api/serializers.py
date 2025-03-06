from django.contrib.auth.models import Group, User
from rest_framework import serializers
from api.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UserProfilSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfil
        fields = '__all__'

class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Discussion
        fields = ['id', 'receiver', 'createdBy', 'state']


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class CompetenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Competence
        fields = ['id', 'title']