from django.shortcuts import render
from django.http import HttpResponse

import rest_api.aws as aws

def index(request):
    return HttpResponse("ok")