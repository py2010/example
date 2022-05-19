# coding=utf-8
import logging

from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .base import MyMixin
logger = logging.getLogger()


class FormMixin:

    # def get_form_class(self):
    #     if self.form_class is None and self.fields is None:
    #         self.fields = '__all__'
    #     return super().get_form_class()

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

