from django.shortcuts import render
from django.http import HttpResponse

from .models import Publication, Comment, Profile
from .serializers import ProfileSerializer, UserSerializer, PublicationSerializer
from rest_framework import viewsets, status
from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.contrib import auth

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseForbidden, Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404


def index(request):
    return HttpResponse("ok")


def login(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # Redirect to a success page.
            return HttpResponse()
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


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        if request.method == 'POST' and request.path == '/api/profile/':
            return
        return SessionAuthentication.enforce_csrf(self, request)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
        
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def create(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid() and \
            'password' in request.POST and \
                len(request.POST['password']) > 0:
            serializer.validated_data.update({
                'password': request.POST['password']
            })
            serializer.create(serializer.validated_data)
        else:
            return Response(status=400, data=serializer.errors)
        return Response(serializer.data)

    # def partial_update(self, request, pk=None):
    #     serializer = ProfileSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.update(get_object_or_404(
    #             Profile, user=request.user), serializer.validated_data)
    #     return Response(serializer.data)

    # def update(self, request, pk=None):
    #     serializer = ProfileSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.update(get_object_or_404(
    #             Profile, user=request.user), serializer.validated_data)
    #     return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def set_password(self, request):
        try:
            user = request.user
            user.set_password(request.POST['password'])
            user.save()
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
    permission_classes = [permissions.IsAuthenticated]
