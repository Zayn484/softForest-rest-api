from django.contrib import admin
from . import models


class ProjectFileInline(admin.TabularInline):
    model = models.ProjectFile
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'price', 'discount_rate']
    actions = ['discount_30', 'deactivate_discount']
    inlines = [ProjectFileInline]

    def discount_30(self, request, queryset):

        discount = 30.00

        for project in queryset:
            """ Set discount of 30%"""
            multiplier = discount / 100
            old_price = float(project.price)
            new_price = old_price - (old_price * multiplier)
            project.discount_rate = round(new_price, 2)
            project.on_sale = True
            project.save(update_fields=['discount_rate', 'on_sale'])
    discount_30.short_description = 'Set 30%% discount'

    def deactivate_discount(self, request, queryset):

        for project in queryset:
            """ Setting discount back to 0.00"""
            project.discount_rate = 0.00
            project.on_sale = False
            project.save(update_fields=['discount_rate', 'on_sale'])
    deactivate_discount.short_description = 'Deactivate discount'

    class Meta:
        model = models.Project


# Register your models here.
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Module)
admin.site.register(models.Technology)
admin.site.register(models.Requirement)
admin.site.register(models.Snapshot)
admin.site.register(models.ProjectFile)