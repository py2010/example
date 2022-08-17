# coding=utf-8
import logging

from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.forms.models import ModelChoiceField

from .base import MyMixin
logger = logging.getLogger()


class FormMixin:

    # def get_form_class(self):
    #     if self.form_class is None and self.fields is None:
    #         self.fields = '__all__'
    #     return super().get_form_class()

    def get_form(self, form_class=None):
        # 大数据表外键, 未自定义视图/模型FORM/模板, 编辑页默认的ModelForm打开太慢
        form = super().get_form(form_class)
        for name, field in form.fields.items():
            if hasattr(field, 'queryset'):
                if isinstance(field, ModelChoiceField):
                    # 外键大数据只显示前面1000条
                    n = 1000
                    qs = field.queryset[:n]
                    if qs.count() >= n:
                        logger.warning(
                            f'大数据页面为了性能, {qs.model}表超出{n}条后的数据将不显示,'
                            '请按需自定义视图/模板, 比如带搜索功能的Ajax二次请求大表数据'
                        )
                        field.queryset = qs
                else:
                    # 多对多
                    pass
        return form

    def get_success_url(self):
        # 保存完成后, 跳转url
        try:
            if self.success_url:
                return str(self.success_url)
        except Exception:
            logger.error('取跳转URL出错:', exc_info=True)

        # success_url未配置或错误配置, 跳转到列表页
        view_name = self.request.resolver_match.view_name  # app_name可能和meta.app_label不同
        list_view_name = f'{view_name[:-6]}list'
        return reverse_lazy(list_view_name)


class MyCreateView(MyMixin, FormMixin, CreateView):
    1


class MyUpdateView(MyMixin, FormMixin, UpdateView):
    1

