from django.contrib import admin
from .models import Request, File


class FileInline(admin.TabularInline):
    model = File
    extra = 1


class Admin(admin.ModelAdmin):
    list_display = ['__str__', 'user']
    inlines = [FileInline]

    class Meta:
        model = Request


# Register your models here.
admin.site.register(Request, Admin)
