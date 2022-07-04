# coding=utf-8
import logging

from django.http import JsonResponse
from django.views.generic import View, DetailView
# from django.db.models.constants import LOOKUP_SEP

import traceback
from django.db.models import Manager
from django.db.models.fields import reverse_related
from django.db.models.fields import related

from django.contrib.admin import utils
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from .base import MyMixin
from .edit import MyCreateView, MyUpdateView
from .list import MyListView
from ..conf import EMPTY_VALUE_DISPLAY
logger = logging.getLogger()

__all__ = [
    'MyCreateView', 'MyDeleteView', 'MyUpdateView', 'MyListView', 'MyDetailView',
    'lookup_val'

]


class MyDeleteView(MyMixin, View):
    '''批量删除model表数据'''

    def post(self, request, *args, **kwargs):
        error = ''
        ids = request.POST.getlist('id', [])
        if ids:
            try:
                self.model._default_manager.filter(id__in=ids).delete()
            except Exception as e:
                error = str(e)
        else:
            error = '未提供删除对象id, 操作忽略'

        return JsonResponse({
            'status': False if error else True,
            'error': error
        })


class MyDetailView(MyMixin, DetailView):
    # template_name = "generic/_detail.html"

    def get_context_data(self, **kwargs):
        """生成各字段key/val，以便在模板中直接使用"""
        context = super().get_context_data(**kwargs)
        self.object.fields_list = []
        for field in self.object._meta.fields:
            val = obj_get_val(self.object, field)
            self.object.fields_list.append((field.verbose_name or field.attname, val or EMPTY_VALUE_DISPLAY))
        return context


def lookup_val(obj, field_info):
    '''
    ListView 获取 object.field_name 值, 支持多层关联表路径字段 xx__xxx__xx
    field_info: field_path, verbose_name, field
    '''
    field_path, verbose_name, last_field_name, fields = field_info
    if not fields:
        # ListView.list_fields 为空或无任何有效字段, 返回obj本身
        return obj

    try:
        field_names = field_path.split('__')
        for field_name in field_names[:-1]:
            # 循环取关联表数据
            if field_name.startswith('~'):
                # 虚拟关联字段
                field_name = field_name[1:]
                obj = get_attr(obj, '_vr')
            obj = get_attr(obj, field_name)
            if not obj:
                return EMPTY_VALUE_DISPLAY

        if field_names[-1].startswith('~'):
            field_name = field_names[-1][1:]  # 最后一个字段为虚拟关联字段
            val = get_attr(obj, '_vr', field_name)
        else:
            if isinstance(obj, Manager):
                obj = obj.all()
            if hasattr(obj, '__iter__'):
                val = display_qs([obj_get_val(i, fields[-1], last_field_name) for i in set(obj) if i])
            else:
                val = obj_get_val(obj, fields[-1], last_field_name)
        return val or EMPTY_VALUE_DISPLAY

    except Exception:
        traceback.print_exc()


def get_attr(obj, *names):
    for name in names:
        if isinstance(obj, Manager):
            obj = obj.all()
        if hasattr(obj, '__iter__') and not isinstance(obj, str):
            obj = [getattr(i, name) for i in set(obj)]
        else:
            obj = getattr(obj, name)
    return obj


def obj_get_val(obj, field, source_field_name=None):
    '''
    从obj 获取 obj.field_name 值.
    source_field_name, 外键/o2o字段不管是field_name还是field_name_id, field对象都一样,
    所以用于list_fields区分返回obj.关联对象, 还是返回数据库值obj.field_name_id
    '''
    # return field.value_from_object(obj)
    # import ipdb; ipdb.set_trace()  # breakpoint b1d5cabb //
    try:
        value = ''
        # if isinstance(field, fields.mixins.FieldCacheMixin):  # django 1.x不支持
        if isinstance(field, related.RelatedField):
            # 正向关系字段

            if isinstance(field, related.ManyToManyField):
                # 多对多字段
                qs = getattr(obj, field.name).all()
                return display_qs(qs)
            else:
                # (N对一) 外键/一对一, 注意区分 field.name 与带"_id"的 field.attname
                # 如果是field.attname, 不使用关联表数据, 而是当前表关联字段值
                try:
                    value = getattr(obj, source_field_name or field.name)
                except ObjectDoesNotExist:
                    value = getattr(obj, {field.attname})  # 取数据库字段值

        elif isinstance(field, reverse_related.ForeignObjectRel):
                # 反向关系字段

            related_name = field.get_accessor_name()
            rel_obj = getattr(obj, related_name, None)
            if rel_obj is None:
                return
            if isinstance(field, reverse_related.OneToOneRel):
                    # 反向OneToOne字段
                value = rel_obj
            elif isinstance(field, (
                reverse_related.ManyToOneRel,
                reverse_related.ManyToManyRel,
            )):
                # (N对多) 反向外键/反向m2m字段, 对应多条obj数据.
                # qs = rel_obj.all()
                return display_qs(rel_obj)
        if not value:
            # 普通字段, 或外键字段/正反一对一字段
            value = getattr(obj, field.name)

        display_value = utils.display_for_field(value, field, value)

        return display_value

    except Exception:
        traceback.print_exc()


def display_qs(qs):
    if isinstance(qs, Manager):
        qs = qs.all()
    return format_html('<br/>'.join([str(obj) for obj in qs]))


'''
# 使用示例:

class XxxMixin:
    model = models.Xxx


class XxxList(XxxMixin, views.MyListView):
    list_fields = ['pk', 'm2o__o2o__pk', 'x2o__x2m', '反向外键/正反m2m']
    filter_fields = ['field1', 'x2o__field3']
    filter_orm_fields = '__all__'


class XxxDetail(XxxMixin, views.MyDetailView):
    1


class XxxForm(XxxMixin):
    fields = '__all__'
    # form_class = forms.XxxForm


class XxxCreate(XxxForm, CreateView):
    # template_name_suffix = '_add'
    1


class XxxUpdate(XxxForm, UpdateView):
    1


class XxxDelete(XxxMixin, views.MyDeleteView):
    1


# URL人工配置示例

from django.conf.urls import url
from xxx_app_label import views

urlpatterns = [

    url(r'^xxx/create/$', views.XxxAdd.as_view(), name='xxx_create'),
    url(r'^xxx/delete/$', views.XxxDelete.as_view(), name='xxx_delete'),

    url(r'^xxx/(?P<pk>\d+)/update/$', views.XxxUpdate.as_view(), name='xxx_update'),

    url(r'^xxx/(?P<pk>\d+)/$', views.XxxDetail.as_view(), name='xxx_detail'),
    url(r'^xxx/$', views.XxxList.as_view(), name='xxx_list'),

]

# 自动生成URL配置及视图示例, 参考 generic.routers.MyRouter

'''
