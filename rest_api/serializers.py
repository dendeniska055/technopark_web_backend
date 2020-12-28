from .models import Publication, Profile, Subscription, Comment, Like, Tag
from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework.validators import UniqueValidator

from datetime import datetime


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    birthday = serializers.DateField(required=True)
    description = serializers.CharField(required=False, default='')

    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all())]
                                   )
    username = serializers.CharField(required=True,
                                     validators=[UniqueValidator(
                                         queryset=User.objects.all())]
                                     )
    photo = serializers.FileField(required=False)

    def create(self, validated_data):
        profile = Profile.objects.create(
            user=validated_data['user'],
            birthday=validated_data['birthday'],
            description=validated_data.get('description', ''),
        )
        if 'photo' in validated_data.keys():
            profile.photo = validated_data['photo']
        return profile

    def update(self, instance, validated_data):
        instance.photo = validated_data.get('photo', instance.photo)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = [
            'birthday',
            'avatar',
            'description',
            # 'users'
        ]


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(
        min_length=1,
        required=False,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        if attrs['username'].isdigit() == True:
            raise serializers.ValidationError({'username':
                                               'Имя пользователя не может быть числом'})
        return attrs

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        try:
            tmp = int(validated_data.username)
            assert False
        except:
            pass
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    user = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False,
        read_only=True,
        default=serializers.CurrentUserDefault())
    description = serializers.CharField(required=False)
    date = serializers.DateTimeField(read_only=True,
                                     default=serializers.CreateOnlyDefault(
                                         datetime.now)
                                     )
    photo = serializers.FileField(required=True)

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Tag.objects.all(),
        allow_null=True)

    # likes = serializers.IntegerField(read_only=True)
    # like = serializers.BooleanField(read_only=True)

    class Meta:
        model = Publication
        fields = "__all__"


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    subscriber = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    date = serializers.DateTimeField(read_only=True,
                                     default=serializers.CreateOnlyDefault(
                                         datetime.now)
                                     )

    class Meta:
        model = Subscription
        fields = "__all__"


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    publication = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Publication.objects.all())
    comment = serializers.CharField(required=True)
    date = serializers.DateTimeField(read_only=True,
                                     default=serializers.CreateOnlyDefault(
                                         datetime.now)
                                     )

    class Meta:
        model = Comment
        fields = "__all__"


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    publication = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Publication.objects.all(), allow_null=True)
    comment = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Comment.objects.all(), allow_null=True)
    date = serializers.DateTimeField(read_only=True,
                                     default=serializers.CreateOnlyDefault(
                                         datetime.now)
                                     )

    def validate(self, attrs):
        if attrs['publication'] is not None and attrs['comment'] is not None:
            raise serializers.ValidationError(
                'Лайк задан и для публикации, и для комметнария, может быть только один вариант')
        if attrs['publication'] is None and attrs['comment'] is None:
            raise serializers.ValidationError(
                'Лайк не задан ни для публикации, ни для комметнария')
        return attrs

    class Meta:
        model = Like
        fields = "__all__"


class TagSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    publication = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Publication.objects.all(),
        allow_null=True
    )
    title = serializers.CharField(
        required=True,
        max_length=128,
        validators=[UniqueValidator(
            queryset=Tag.objects.all())]
    )

    class Meta:
        model = Tag
        fields = "__all__"
