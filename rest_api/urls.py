from django.conf.urls import url
from rest_api import views
from django.urls import path
app_name = 'rest_api'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('get_my_id/', views.get_my_id, name="get_my_id"),
]
