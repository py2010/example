# from django.shortcuts import render
from generic import views

from . import models
from a import models as a_models
# Create your views here.


class DemoList(views.ModelMixin, views.MyListView):
    model = models.Demo
    list_fields = [
        'name',
        ('p_id', '跨库外键ID'),
        'one_id',
    ]

    def get_queryset(self):
        # 合并
        qs = super().get_queryset()
        p_ids = [o.p_id for o in qs]  # qs._fetch_all()
        # virtual_join
        qs_p = a_models.P.objects.filter(id__in=p_ids)  # 数据表大时, 可过滤优化SQL.
        qs_o = a_models.One._default_manager.all()

        objs = self.virtual_join(qs, qs_p, rel_field='p_id')  # 跨库关联"外键"
        objs = self.virtual_join(objs, qs_o, rel_field='one_id')  # 跨库关联"o2o"

        # virtual_m2m
        demo_ids = [o.id for o in qs]  # qs._result_cache
        qs_middle = models.Middle._default_manager.filter(demo_id__in=demo_ids)  # 若为大表可过滤限定ID
        t_ids = [o.t_id for o in qs_middle]  # qs_middle._fetch_all()
        qs_t = a_models.T._default_manager.all()  # 若为大表可限定ID
        # 跨库关联m2m
        objs = self.virtual_m2m(objs, qs_middle, qs_t, m_rel_field_1='demo_id', m_rel_field_2='t_id')

        # import ipdb; ipdb.set_trace()  # breakpoint 0f2850bb //
        return objs

