# coding=utf-8
#
from django.conf.urls import url

from generic.routers import add_router_for_all_models
# from generic.routers import MyRouter

from . import views

urlpatterns = [

    # Demo
    url(r'^demo/$', views.DemoList.as_view(), name="demo_list"),


]


add_router_for_all_models()

# print(urlpatterns)
