"""xyf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
try:
    from django.urls import re_path
except Exception:
    from django.conf.urls import url as re_path  # django 1.*

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from allapp import URLS_APPS
from .views import index, login, logout, password_change

admin.site.site_header = '演示系统后台管理'

urlpatterns = [

    re_path('admin/', admin.site.urls),
    re_path(r'^login', login, name="login"),
    re_path(r'^password_change', password_change, name="password_change"),
    # re_path(r'^otp', otp, name="otp"),
    re_path(r'^logout', logout, name="logout"),


    re_path(r'^$', index),

]

urlpatterns += staticfiles_urlpatterns()


for app, app_urls in URLS_APPS.items():
    # 开始自动装载各app.urls

    app_urlresolver = getattr(app_urls, 'urlpatterns', [])

    app_urlpattern = re_path(f'{app}/', (app_urlresolver, app, app))

    urlpatterns.append(app_urlpattern)

# print(urlpatterns)
# import ipdb;ipdb.set_trace()

