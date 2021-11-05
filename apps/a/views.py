# from django.shortcuts import render

from generic import views
from . import models


class UserMixin(views.ModelMixin):
    model = models.User


class UserList(UserMixin, views.MyListView):
    list_fields = [
        # 'id',
        'username',
        'is_superuser',
        'is_active',
        # 'is_staff',
        'date_joined',
    ]

    # def get_queryset(self):
    #     raise
    #     qs = super().get_queryset()
    #     return qs


class OneMixin(views.ModelMixin):

    model = models.One


class OneList(OneMixin, views.MyListView):
    list_fields = [
        'name',
        't',
        'm',
    ]
    # filter_fields = ['p__name', '', ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class PMixin(views.ModelMixin):

    model = models.P


class PList(PMixin, views.MyListView):
    list_fields = [
        'name',
        # 'desc',
        't_set',
        't',
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        # import ipdb; ipdb.set_trace()
        return qs


class TMixin(views.ModelMixin):

    model = models.T


class TList(TMixin, views.MyListView):
    list_fields = [
        'name',
        'm_set',
        'p__b__name',
    ]

    # def get_queryset(self):
    #     # 演示 - 真实x2o关系, 也可进行虚拟join关联, obj1.save()不影响外键数据
    #     qs = super().get_queryset()
    #     # return qs
    #     qs_o = models.One._default_manager.all()
    #     objs = self.virtual_join(qs, qs_o)
    #     # import ipdb; ipdb.set_trace()  # breakpoint 0f2850bb //
    #     return objs

    def get_queryset(self):
        # 演示 - 虚拟m2m关联
        qs = super().get_queryset()
        qs_m = models.M._default_manager.all()
        qs_m2t = models.M2T._default_manager.all()
        objs = self.virtual_m2m(qs, qs_m2t, qs_m, m_rel_field_1='t_id', m_rel_field_2='m_id')
        # return objs

        # 跨库虚拟关联, 反向外键
        from vr.models import Middle
        qs_middle = Middle.objects.all()
        objs = self.virtual_join(qs, qs_middle, rel_field='t_id', reverse=True)
        # import ipdb; ipdb.set_trace()
        return objs

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        return res

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        return res


class MMixin(views.ModelMixin):

    model = models.M


class MList(MMixin, views.MyListView):
    list_fields = [
        'name',
        't',
        'm2t_set__m',
    ]

    # def get_queryset(self):
    #     # 合并
    #     qs = super().get_queryset()
    #     import ipdb; ipdb.set_trace()  # breakpoint 7630702d //
    #     qs_m = models.M._default_manager.all()
    #     qs_m2t = models.M2T._default_manager.all()
    #     return self.virtual_m2m(qs, qs_m2t, qs_m, m_rel_field_1='t_id', m_rel_field_2='m_id')


class M2TMixin(views.ModelMixin):

    model = models.M2T


class M2TList(M2TMixin, views.MyListView):
    list_fields = [
        'id',
        'm',
        't',
        'm_id',
        't_id',
    ]
    filter_fields = ['t__p__name', ]
    # paginate_by = None

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs
