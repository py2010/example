# from django.shortcuts import render
from generic import views

from . import models
# Create your views here.


class UserList(views.MyListView):
    model = models.User
    list_fields = [
        'id',
        'name',
        'sex',
        ('~p__name', 'P名称'),
        # ('p', 'P'),
        # ('~one__name', 'One名称'),
    ]
    paginate_by = 10
    # cursor_offset_max = 1000  # 数据超过多少条, 自动切换成游标分页 (游标分页最大偏移量)
    paginator_class = views.pagination.NullFieldCursorPaginator  # 游标分页排序字段支持Null数据
    cursor_order_fields = '__all__'  # 允许前端控制排序的字段，列表或'__all__'.


class HostList(views.MyListView):
    model = models.Host
    list_fields = [
        'id',
        ('~p__name', '机组'),
        'name',
        'status',
        'asset_type',
        'remark',
        ('user__name', '用户'),
        # 'update_time',
    ]
    paginate_by = 10
    cursor_offset_max = 600  # 游标分页最大偏移量, 这里为试验效果而设小值
    cursor_unique_field = '-pk'  # 主键或unique=True的字段, 用于生成唯一序列
    cursor_order_fields = '__all__'  # 允许前端控制排序的字段，列表或'__all__'.

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     qs = context['object_list']
    #     return context

