from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Recommendation)
admin.site.register(models.Profile)
