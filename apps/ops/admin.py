# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Permission

# from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType


from . import models


@admin.register(models.UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', 'weixin', 'phone')
    search_fields = ('username', 'name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


'''
django-admin增加显示权限表
'''


def get_model_label(obj):
    # import ipdb;ipdb.set_trace()
    model_class = obj.model_class()
    if model_class:
        return '%s / %s' % (model_class._meta.app_config.verbose_name, str(model_class._meta.verbose_name))
    else:
        # 对应模型已删除
        return ''


ContentType.__str__ = get_model_label
ContentType._meta.ordering = ['app_label', 'model']
# ContentType._meta.default_manager.get_queryset
# import ipdb;ipdb.set_trace()


@admin .register(ContentType)
class ContentTypeAdmin (admin .ModelAdmin):
    list_display = ('label', 'app_label', 'model')
    search_fields = ('app_label', 'model')

    def label(self, obj):
        # 增加虚拟字段, 显示app/model对应中文标识
        return get_model_label(obj)

    label.short_description = '模型名'


@admin .register(Permission)
class PermissionAdmin (admin .ModelAdmin):
    list_filter = ('content_type',)
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name', 'codename')


# @admin .register(LogEntry)
# class LogEntryAdmin (admin .ModelAdmin):
#     list_display = ('content_type', 'action_flag', 'user', 'action_time')
#     list_filter = ('user', 'content_type', 'action_flag', 'action_time')
