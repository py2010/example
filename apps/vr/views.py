# from django.shortcuts import render
from generic import views

from . import models
# Create your views here.


class DemoList(views.MyListView):
    model = models.Demo
    list_fields = [
        'name',
        ('p_id', 'p_ID'),
        ('~p__name', 'p虚拟外键'),
        ('one_id', 'one_ID'),
        ('~one__name', 'one虚拟一对一'),
        ('~middle__id', '中间表id'),
        ('~middle__~t__name', 'T (虚拟多对多)'),
        ('~middle__~t__one__name', '测试SQL效果'),
    ]
