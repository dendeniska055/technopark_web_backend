from django.conf.urls import url
from rest_api import views
from django.urls import path
app_name = 'rest_api'

urlpatterns = [
    path('', views.index, name='index')
]
