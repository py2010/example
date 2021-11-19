# from django.shortcuts import render
from generic import views

from . import models
from a import models as a_models
# Create your views here.


class DemoList(views.MyListView):
    model = models.Demo
    list_fields = [
        'name',
        ('p_id', '跨库外键ID'),
        'one_id',
    ]

    def vr(self, queryset):
        # 跨库关联演示，关联表qs2.all() 自动过滤不必要的数据，这里所有关联表直接提供all()所有，会自动过滤
        # 比如 http://127.0.0.1:808/vr/demo/?pagesize=1 只显示一条obj1数据，各关联表只查所需值。

        # virtual_join
        qs_p = a_models.P.objects.all()
        qs_o = a_models.One._default_manager.all()

        objs = self.virtual_join(queryset, qs_p, rel_field='p_id')  # 跨库关联"外键"
        objs = self.virtual_join(objs, qs_o, rel_field='one_id')  # 跨库关联"o2o"

        # virtual_m2m
        qs_middle = models.Middle._default_manager.all()
        qs_t = a_models.T._default_manager.all()
        # 跨库关联m2m
        objs = self.virtual_m2m(objs, qs_middle, qs_t, m_rel_field_1='demo_id', m_rel_field_2='t_id')

        # import ipdb; ipdb.set_trace()  # breakpoint 0f2850bb //
        return objs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = self.vr(context['object_list'])  # 跨库关联
        return context
