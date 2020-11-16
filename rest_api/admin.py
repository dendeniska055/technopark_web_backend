from django.contrib import admin
from rest_api import models

admin.site.register(models.Profile)
admin.site.register(models.Publication)
admin.site.register(models.Pictures)
admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.Tag)
admin.site.register(models.Subscription)