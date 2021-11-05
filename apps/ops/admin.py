# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin

from . import models


@admin.register(models.UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', 'weixin', 'phone')
    search_fields = ('username', 'name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

