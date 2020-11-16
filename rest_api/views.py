from django.shortcuts import render
from django.http import HttpResponse

from .models import Publication, Comment
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, PublicationSerializer
from django.contrib.auth.models import User


def index(request):
    return HttpResponse("ok")


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [permissions.IsAuthenticated]
