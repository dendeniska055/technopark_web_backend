from django.shortcuts import render
from django.http import HttpResponse

from .models import Publication, Comment, Profile, Subscription, Like, Tag
from .serializers import *
from rest_framework import viewsets, status, mixins
from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.contrib import auth

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseForbidden, Http404, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.parsers import FileUploadParser

from django.db.models import Q, Count

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


def index(request):
    return HttpResponse("ok")


def login(request):
    if request.user.is_authenticated:
        return HttpResponse(request.user.id)
    try:
        if 'email' in request.POST.keys():
            username = User.objects.get(email=request.POST['email']).username
        else:
            username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # Redirect to a success page.
            return HttpResponse(request.user.id)
        else:
            return HttpResponseForbidden()
    except:
        return HttpResponseBadRequest()


def logout(request):
    try:
        auth.logout(request)
        return HttpResponse()
    except:
        return HttpResponseBadRequest()


def get_my_id(request):
    if request.user.is_authenticated:
        return HttpResponse(request.user.id)
    return HttpResponseForbidden()


# user = User.objects.get(id=16)
# user.set_password('deniskaden055')
# user.username = 'denis'
# user.save()


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        if request.method == 'POST' and request.path == '/api/profile/':
            return
        return SessionAuthentication.enforce_csrf(self, request)


class IsUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST' and request.path == '/api/profile/':
            return True
        if type(obj) == Tag:
            return True  # ИСПРАВИТЬ !!!!!!!!!!!!!!!!!!!!!!
        return obj.user == request.user


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsUserOrReadOnly]
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)
    filter_backends = [SearchFilter]
    search_fields = ['^user__username']

    def retrieve(self, request, pk=None):
        try:
            id = int(pk)
            profile = get_object_or_404(Profile, user__id=id)
        except:
            profile = get_object_or_404(Profile, user__username=pk)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data.update({
            'id':profile.user.id
        })
        return JsonResponse(data)

    def create(self, request):
        if request.user.is_authenticated:
            return Response(status=400, data='Already auth')

        serializer = ProfileSerializer(data=request.data)
        users_serializer = UserSerializer(data=request.data)
        user = -1
        if serializer.is_valid() and \
                users_serializer.is_valid() and \
                'password' in users_serializer.validated_data.keys():
            user = users_serializer.create(users_serializer.validated_data)
            user.set_password(users_serializer.validated_data['password'])
            user.save()
            auth.login(request, user)

            serializer.validated_data.update({
                'user': user
            })

            serializer.create(serializer.validated_data)
        else:
            if not users_serializer.is_valid():
                return Response(status=400, data=users_serializer.errors)
            serializer.errors.update(users_serializer.errors)
            if 'password' not in users_serializer.validated_data.keys():
                return Response(status=400, data={
                    'password': 'Обязательный параметр для регистрации'
                })
            return Response(status=400, data=serializer.errors)
        send_data = serializer.data
        send_data.update({"id": request.user.id})
        return Response(send_data)

    def partial_update(self, request, pk=None):
        serializer = ProfileSerializer(data=request.data)
        users_serializer = UserSerializer(data=request.data)
        if serializer.is_valid() and users_serializer.is_valid():
            users_serializer.update(
                request.user, users_serializer.validated_data)
            serializer.update(get_object_or_404(
                Profile, user=request.user), serializer.validated_data)
            return Response(serializer.data)
        return Response(status=400, data=serializer.errors)

    def update(self, request, pk=None):
        serializer = ProfileSerializer(data=request.data)
        users_serializer = UserSerializer(data=request.data)
        if serializer.is_valid() and users_serializer.is_valid():
            users_serializer.update(
                request.user, users_serializer.validated_data)
            serializer.update(get_object_or_404(
                Profile, user=request.user), serializer.validated_data)
            return Response(serializer.data)
        return Response(status=400, data=serializer.errors)

    @action(detail=False, methods=["post"])
    def set_password(self, request):
        try:
            user = request.user
            user.set_password(request.POST['password'])
            user.save()

            auth.login(request, user)

            return Response()
        except:
            return HttpResponseBadRequest()

    # @action(detail=True)
    # def recent_users(self, request):
    #     recent_users = User.objects.all().order_by('-last_login')

    #     page = self.paginate_queryset(recent_users)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(recent_users, many=True)
    #     return Response(serializer.data)


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsUserOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user', 'tags']
    search_fields = ['=tags__title']


    @action(detail=False, methods=["get"])
    def get_feed(self, request):
        try:
            user = request.user
            subscriptions = Subscription.objects.values_list('subscriber').filter(user=user)
            publications = Publication.objects.filter(user__in=subscriptions)
            
            page = self.paginate_queryset(publications)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(publications, many=True)
            return Response(serializer.data)
        except:
            return HttpResponseBadRequest()

    @action(detail=True, methods=["get"])
    def get_likes(self, request, pk):
        try:
            user = request.user
            likes_count = Like.objects.filter(publication__pk=pk).count()
            like = Like.objects.filter(
                user=user, publication__pk=pk).count() == 1
            return Response(data={
                'likes_count': likes_count,
                'like': like
            })
        except:
            return HttpResponseBadRequest()

    @action(detail=True, methods=["get"])
    def get_tags(self, request, pk):
        tags = get_object_or_404(Publication, pk=pk).tags.values('id', 'title').all()
        print(tags)
        return Response(data=tags)
        # try:
        # except:
        #     return HttpResponseBadRequest()

    @action(detail=True, methods=["post"])
    def set_like(self, request, pk):
        try:
            user = request.user
            if 'set' not in request.data.keys() or \
                    (request.data['set'] != 'dislike' and request.data['set'] != 'like'):
                return Response(status=400, data='set - requered props (like or dislike)')

            like = True
            if request.data['set'] == 'dislike':
                like = False

            publication = get_object_or_404(Publication, pk=pk)
            this_publ_like = Like.objects.filter(
                user=user, publication=publication)
            get_like = len(this_publ_like) == 1
            if get_like == like:
                return Response(status=400, data='Статус уже принят')

            if like == True:
                Like.objects.create(user=user, publication=publication)
            else:
                this_publ_like.delete()
            return Response()
        except:
            return HttpResponseBadRequest()


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsUserOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'subscriber']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsUserOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['publication']


# class LikeViewSet(viewsets.ModelViewSet):
#     queryset = Like.objects.all()
#     serializer_class = LikeSerializer
#     permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]
#     authentication_classes = [SessionAuthentication, BasicAuthentication]


class TagViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsUserOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    filter_backends = [SearchFilter]
    search_fields = ['^title']

    def list(self, request):
        try:
            tags = Tag.objects.values('id', 'title')
            if 'search' in request.GET.keys():
                tags = tags.filter(title__istartswith=request.GET['search'])
            elif 'get' in request.GET.keys():
                tags = tags.filter(title=request.GET['get'])
            else:
                tags = tags.all()
            print(tags)
            page = self.paginate_queryset(tags)
            if page is not None:
                return self.get_paginated_response(page)

            serializer = self.get_serializer(tags, many=True)
            return Response(serializer.data)
        except:
            return HttpResponseBadRequest()
