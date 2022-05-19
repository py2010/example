# coding=utf-8
import logging

from django.views import generic
from django.utils.decorators import classonlymethod
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from django.db.models.constants import LOOKUP_SEP

logger = logging.getLogger()


class ModelMixin:
    '''
    给cls设置属性: model
    '''
    model = None
    queryset = None

    @classonlymethod
    def as_view(cls, **initkwargs):
        cls._renew_()
        return super().as_view(**initkwargs)

    @classonlymethod
    def _renew_(cls):
        # 用于给ModelView设置属性
        if not cls.model:
            if not cls.queryset:
                raise Exception(f'{cls}: Model View ??')
            else:
                cls.model = cls.queryset.model


class TemplateMixin(ModelMixin):
    '''
    给cls设置属性: model_meta, template_name
    '''

    @classonlymethod
    def _renew_(cls):
        super()._renew_()
        cls.model_meta = ops = cls.model._meta  # 由于模板中禁止访问"_"开头的属性.

        if hasattr(cls, 'get_template_names'):
            # 自动设置模板页
            def get_template_names(self):
                '''
                django-ListView 是从object_list 中取model, 而不是取view.model
                object_list 如果不是QuerySet, 比如虚拟关联处理后qs已转为obj列表,
                从object_list取不到model, 无法生成model_template, 所以替换函数.
                '''
                try:
                    templates = super().get_template_names()
                except Exception:
                    # traceback.print_exc()  # django 2.*
                    templates = []

                model_template = f'{ops.app_label}/{ops.model_name}{self.template_name_suffix}.html'
                generic_template = f'generic/{self.template_name_suffix}.html'

                logger.debug(f'\r\nmodel_template name: {model_template} \r\ngeneric_template name: {generic_template}')
                # logger.debug(f'\r\nmodel_template: {model_template} \r\ngeneric_template: {generic_template}')
                # 优先使用自定义模板 model_template
                if model_template not in templates:
                    templates.append(model_template)

                if generic_template not in templates:
                    templates.append(generic_template)

                return templates
            cls.get_template_names = get_template_names


class AuthMixin(LoginRequiredMixin, PermissionRequiredMixin, ModelMixin):
    '''
    给cls设置属性: permission_required
    '''

    @classonlymethod
    def _renew_(cls):
        super()._renew_()
        if not cls.permission_required:
            # 自动设置权限代码
            if issubclass(cls, generic.CreateView):
                action = 'add'  # 增
            elif issubclass(cls, generic.UpdateView):
                action = 'change'  # 改
            elif issubclass(cls, (generic.ListView, generic.DetailView)):
                action = 'view'  # 查
            else:
                action = 'delete'  # 删

            ops = cls.model._meta
            cls.permission_required = f'{ops.app_label}.{action}_{ops.model_name}'
            # print(cls, cls.permission_required, 77777)


# class MyPermissionRequiredMixin(PermissionRequiredMixin):
#     '''
#     django的PermissionRequiredMixin不按request.method请求类型进行区分权限,
#     GET/POST/DELETE之前都是先dispatch判断权限, 所以重写使支持Restful方式的权限
#     '''

#     def get_permission_required(self):
#         method = self.request.method  # 根据method返回相应权限


class MyMixin(AuthMixin, TemplateMixin):
    '''
    由于不想在MyListView/MyDetailView等View中分别重写as_view(), 所以统一在当前重写.
    多重继承时注意顺序, python中越往右为越远的基类祖先, 和VUE中继承顺序书写相反.
    '''

