# coding=utf-8
#
from django.conf.urls import url

# from generic.routers import add_router_for_all_models
from generic.routers import MyRouter
from . import models
from . import views

urlpatterns = [


    # User
    url(r'^user/$', views.UserList.as_view(), name="user_list"),
    *MyRouter(
        models.User,
        list=False,
        delete=False,
    ),

    # One
    url(r'^one/$', views.OneList.as_view(), name="one_list"),
    *MyRouter(models.One, detail=False),

    # P
    url(r'^p/$', views.PList.as_view(), name="p_list"),
    *MyRouter(models.P),


    # T
    url(r'^t/$', views.TList.as_view(), name="t_list"),
    *MyRouter(models.T),


    # M
    url(r'^m/$', views.MList.as_view(), name="m_list"),
    *MyRouter(models.M),


    # M2T
    url(r'^m2t/$', views.M2TList.as_view(), name="m2t_list"),
    *MyRouter(
        models.M2T,
        # delete=False,
    ),

    # # M2T
    # url(r'^m2t/create/$', views.M2TCreate.as_view(), name="m2t_create"),
    # url(r'^m2t/delete/$', views.M2TDelete.as_view(), name="m2t_delete"),

    # url(r'^m2t/(?P<pk>\d+)/update/$', views.M2TUpdate.as_view(), name="m2t_update"),

    # url(r'^m2t/(?P<pk>\d+)/$', views.M2TDetail.as_view(), name="m2t_detail"),
    # url(r'^m2t/$', views.M2TList.as_view(), name="m2t_list"),

]

# print(urlpatterns)

# add_router_for_all_models()
