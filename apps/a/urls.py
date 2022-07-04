# coding=utf-8
#
try:
    from django.urls import re_path
except Exception:
    from django.conf.urls import url as re_path  # django 1.*

# from generic.routers import add_router_for_all_models
from generic.routers import MyRouter
from . import models
from . import views

urlpatterns = [


    # User
    re_path(r'^user/$', views.UserList.as_view(), name="user_list"),
    *MyRouter(
        models.User,
        list=False,
        delete=False,
    ),

    # One
    re_path(r'^one/$', views.OneList.as_view(), name="one_list"),
    *MyRouter(models.One, detail=False),

    # P
    re_path(r'^p/$', views.PList.as_view(), name="p_list"),
    *MyRouter(models.P),

    re_path(r'^p2/$', views.P2List.as_view(), name="p2_list"),
    *MyRouter(models.P2),

    re_path(r'^p3/$', views.P3List.as_view(), name="p3_list"),
    *MyRouter(models.P3, create=False),


    # T
    re_path(r'^t/$', views.TList.as_view(), name="t_list"),
    *MyRouter(models.T),


    # M
    re_path(r'^m/$', views.MList.as_view(), name="m_list"),
    *MyRouter(models.M),


    # M2T
    re_path(r'^m2t/$', views.M2TList.as_view(), name="m2t_list"),
    *MyRouter(
        models.M2T,
        # delete=False,
    ),

    # # M2T
    # re_path(r'^m2t/create/$', views.M2TCreate.as_view(), name="m2t_create"),
    # re_path(r'^m2t/delete/$', views.M2TDelete.as_view(), name="m2t_delete"),

    # re_path(r'^m2t/(?P<pk>\d+)/update/$', views.M2TUpdate.as_view(), name="m2t_update"),

    # re_path(r'^m2t/(?P<pk>\d+)/$', views.M2TDetail.as_view(), name="m2t_detail"),
    # re_path(r'^m2t/$', views.M2TList.as_view(), name="m2t_list"),

]

# print(urlpatterns)

# add_router_for_all_models()
