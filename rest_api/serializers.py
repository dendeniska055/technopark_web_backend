from .models import User, Publication
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"