# coding=utf-8
#
try:
    from django.urls import re_path
except Exception:
    from django.conf.urls import url as re_path  # django 1.*

from generic.routers import MyRouter

from . import views

urlpatterns = [

    re_path(r'^user/$', views.UserListView.as_view(), name="user_list"),
    re_path(r'^host/$', views.HostListView.as_view(), name="host_list"),


]


MyRouter.add_router_for_all_models()

# print(urlpatterns)
