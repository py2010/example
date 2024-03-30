# from django.shortcuts import render

from generic import views
from . import models


class UserMixin:
    model = models.User


class UserListView(UserMixin, views.MyListView):
    list_fields = [
        # 'id',
        'username',
        'is_superuser',
        'is_active',
        # 'is_staff',
        'date_joined',
    ]

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs


class OneMixin:

    model = models.One


class OneListView(OneMixin, views.MyListView):
    paginate_by = 2  # 每页条数
    list_fields = [
        'name',
        ('b__name', 'b-name'),
        't',
        # 'm',
        ('~m', '!!m'),
    ]
    filter_fields = [('b__name', 'b名称'), ]


class PMixin:

    model = models.P


class PListView(PMixin, views.MyListView):
    list_fields = [
        'name',
        # # 'desc',
        # 't_set',
        't',  # select * from t
        ('~m__~p__id', 'pid'),
        ('~m__name', 'm'),
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        # import ipdb; ipdb.set_trace()
        return qs


class P2ListView(views.MyListView):
    model = models.P2
    list_fields = [
        'name2',
        ('~p__name', 'p'),
        ('~p__~m__name', 'm'),
    ]


class P3ListView(views.MyListView):
    model = models.P3
    list_fields = [
        'name3',
        ('~p__name', 'p'),
        ('~p__t__name', 't'),
    ]


class TListView(views.MyListView):
    model = models.T
    paginate_by = 5  # 每页条数
    list_fields = [
        'name',
        'm_set',
        ('p__b__name', 'b'),
        ('one__name', 'one__name'),
        ('~one__name', 'one__name'),  # 外键当成虚拟外键
        # ('~one__b__p_set', '!test'),
    ]
    # queryset = models.T.objects.only('one__name')


class MMixin:

    model = models.M


class MListView(MMixin, views.MyListView):
    # paginate_by = None  # 不分页
    filter_fields = [('name', 'M名称'), ('t__name', 'T名称'), ]  # 搜索过滤
    filter_orm_fields = ['t__name__icontains', 't__p__name__icontains', ]  # orm过滤字段, 为安全必须配置字段
    # filter_orm_fields = '__all__'  # 开放所有字段ORM

    list_fields = [
        'name',
        'one_id',
        ('t__p__name', 't_P名称'),
        ('t__name', 'T (多对多)'),  # 中间表 a_m_t
        # # 'p__b__~one',
        # # 'm2t_set__t_id',
        # # 'm2t_set__t__name',
        ('~p__name', 'P虚拟外键'),
        '~one__b_id',
        '~one__b__p_set',
        ('~m2t_set__~t__name', 'T(虚拟多对多)'),  # 中间表 a_m2t, m2m = o2m + m2o
        ('~m2t_set__~t__p__name', 'P'),
    ]

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     # import ipdb; ipdb.set_trace()
    #     return qs


class M2TMixin:

    model = models.M2T


class M2TListView(M2TMixin, views.MyListView):
    list_fields = [
        'id',
        # 'm',
        # 't',
        'm_id',
        't_id',
        ('~m__name', 'M名'),
        ('~t__name', 'T名'),
        ('t__p__name', '表P的名称'),
    ]
    filter_fields = [('t__p__name', '表P的名称'), ]
    # paginate_by = None

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs
