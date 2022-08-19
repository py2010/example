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
# from django.core.exceptions import ObjectDoesNotExist
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
            try:
                val = display_vals(obj_get_val(self.object, field.name, field))
                self.object.fields_list.append((field.verbose_name or field.attname, val))
            except Exception:
                traceback.print_exc()
        return context


def lookup_val(obj, field_info):
    '''
    ListView 获取 object.field_name 值, 支持多层关联表路径字段 xx__xxx__xx
    field_info: field_path, verbose_name, last_field_name, fields
    正常情况下, 从模型实例取字段数据时不应再有SQL查询, 只有自定义模板展示额外字段时才有可能出现where查询
    为了性能, 请根据自定义模板额外的字段, 自定义视图增加字段数据.
    '''
    field_path, verbose_name, last_field_name, fields = field_info
    if not fields:
        # ListView.list_fields 为空或无任何有效字段, 返回obj本身
        return obj

    # vals = attrgetter(obj, *get_attr_names(field_path))
    # return display_vals(vals)
    try:
        names = get_attr_names(field_path)
        objs = attrgetter(obj, *names[:-1])  # 最后一位字段留着格式化结果数据
        vals = itemgetter(set(objs), obj_get_val, names[-1], fields[-1])
        return display_vals(vals)
    except Exception:
        traceback.print_exc()


def get_attr_names(field_path):
    # __字段分隔成属性列表, 支持~虚拟关联字段
    return field_path.replace('~', '_vr__').split('__')


def attrgetter(objs, *names):
    # 从模型实例中多层关联字段循环取数据, objs一维列表
    if isinstance(objs, str) or not hasattr(objs, '__iter__'):
        objs = [objs]
    if names:
        for name in names:
            objs = itemgetter(objs, get_attr, name)
    return objs


def itemgetter(objs, func, *args, **kwargs):
    # 为便于处理, func() 需返回列表, 当前函数最终返回一维列表数据
    vals = []
    for i in set(objs):
        val = func(i, *args, **kwargs)
        vals.extend(val)
    return vals


def get_attr(obj, attr):
    # 从模型实例中取字段数据, 由于可能是x2m字段, 统一返回列表
    if obj:
        sub = getattr(obj, attr, None)
        if isinstance(sub, Manager):
            return [i for i in sub.all()]
        # elif sub is None:
        #     1
        else:
            return [sub]
    return []


def obj_get_val(obj, field_name, field=None):
    # 从模型实例取字段数据, 显示到页面之前先格式化
    vals = attrgetter(obj, field_name)
    if field:
        if isinstance(field, (related.RelatedField, reverse_related.ForeignObjectRel)):
            # 关联字段/虚拟关联字段
            if isinstance(field, related.ForeignKey) and not vals:
                val = getattr(obj, field.attname)
                if val is not None:
                    vals = [val]  # 外键尝试取数据库字段ID值
        else:
            # 普通字段
            vals = [utils.display_for_field(val, field, EMPTY_VALUE_DISPLAY) for val in vals]
    return vals


def display_vals(vals, empty_value_display=EMPTY_VALUE_DISPLAY):
    return format_html('<br/>'.join([
        str(val) for val in vals if val is not None
    ])) or empty_value_display


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

    url(r'^xxx/create/$', views.XxxCreate.as_view(), name='xxx_create'),
    url(r'^xxx/delete/$', views.XxxDelete.as_view(), name='xxx_delete'),

    url(r'^xxx/(?P<pk>\d+)/update/$', views.XxxUpdate.as_view(), name='xxx_update'),

    url(r'^xxx/(?P<pk>\d+)/$', views.XxxDetail.as_view(), name='xxx_detail'),
    url(r'^xxx/$', views.XxxList.as_view(), name='xxx_list'),

]

# 自动生成URL配置及视图示例, 参考 generic.routers.MyRouter

'''
