# coding=utf-8
#
try:
    from django.urls import re_path
except Exception:
    from django.conf.urls import url as re_path  # django 1.*

from generic.routers import MyRouter

from . import views

urlpatterns = [

    # Demo
    re_path(r'^demo/$', views.DemoListView.as_view(), name="demo_list"),


]


MyRouter.add_router_for_all_models()

# print(urlpatterns)
