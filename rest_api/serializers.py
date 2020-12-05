from .models import Publication, Profile, Pictures
from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework.validators import UniqueValidator


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    # user = serializers.PrimaryKeyRelatedField(
    #     read_only=True)
    birthday = serializers.DateField(required=True)
    avatar = serializers.PrimaryKeyRelatedField(
        queryset=Pictures.objects.all(), required=False)
    description = serializers.CharField(required=False, default='')

    email = serializers.EmailField(required=True,
                                #    validators=[UniqueValidator(
                                #        queryset=User.objects.all())]
                                )
    username = serializers.CharField(required=True,
                                    #  validators=[UniqueValidator(
                                    #      queryset=User.objects.all())]
                                     )
    # password = serializers.CharField(
    #     required=False, style={'input_type': 'password'}, default='')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        
        profile = Profile.objects.create(
            user=user,
            birthday=validated_data['birthday']
        )
        if 'description' in validated_data.keys():
            profile.description = validated_data['description']
            profile.save()
        if 'avatar' in validated_data.keys():
            profile.avatar = Pictures.objects.get(id=validated_data['avatar'])
            profile.save()
        return profile

    def update(self, instance, validated_data):
        _user = instance.user
        _user.email = validated_data.get('email', _user.email)
        _user.username = validated_data.get('username', _user.username)
        _user.save()
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

    # users = serializers.HyperlinkedRelatedField(
    #     view_name='user',
    #     lookup_field='username',
    #     # queryset=User.objects.all(),
    #     # many=True,
    #     read_only=True
    # )

    # class Meta:
    #     model = Profile
    #     fields = [
    #         'birthday',
    #         'avatar',
    #         'description',
    #         # 'users'
    #     ]


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `Snippet` instance, given the validated data.
    #     """
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.linenos = validated_data.get('linenos', instance.linenos)
    #     instance.language = validated_data.get('language', instance.language)
    #     instance.style = validated_data.get('style', instance.style)
    #     instance.save()
    #     return instance

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'groups']


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Publication
        fields = "__all__"
