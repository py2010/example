from django.contrib import admin

from . import models


@admin.register(models.P)
class PAdmin(admin.ModelAdmin):

    list_display = ('name', )


@admin.register(models.T)
class TAdmin(admin.ModelAdmin):

    list_display = ('name', )


@admin.register(models.M)
class MAdmin(admin.ModelAdmin):

    list_display = ('name', )



