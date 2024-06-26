# coding=utf-8
#
# from django.conf.urls import url

from generic.routers import MyRouter

urlpatterns = [

]


actions = {
    # 'update': False,
    'delete': False,
}

'''
批量自动生成model的url和视图
自动生成的url在后, 人工url在前, 同url路径重复时, 前面的人工配置优先.
'''
MyRouter.add_router_for_all_models(**actions)

print('mirror.urlpatterns:', urlpatterns)
