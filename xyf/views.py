# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib import auth
from datetime import datetime
from django.contrib.auth.decorators import login_required


def index(request):
    from config import conf_example as e
    print(dir(e._proxy), 77788888)
    # import ipdb;ipdb.set_trace()

    # print('HTTP_USER_AGENT', request.META.get('HTTP_USER_AGENT'))
    # import os
    # print(os.getpid(), os.getppid(), '..........')
    # raise
    # import traceback
    # traceback.print_stack()
    return render(request, 'base/index.html')


def login(request):
    # import ipdb;ipdb.set_trace()
    # otp_url = '/otp?%s' % request.META.get('QUERY_STRING', '')
    r_url = request.GET.get('next', '/')
    if request.user.is_authenticated:
        if r_url.startswith('/admin') and not request.user.is_staff:
            # 登陆用户无权限访问后台
            r_url = '/'
        return HttpResponseRedirect(r_url)

    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")

        try:
            # 用户密码验证
            user = auth.authenticate(username=u, password=p)
            if user:
                userprofile = user.profile
                if userprofile.chk_userdays():
                    error_msg = "账号过期，已停用，请联系管理员处理"
                else:
                    request.session['login_user_id'] = user.id
                    if userprofile.otp:
                        return HttpResponseRedirect(request.get_full_path())  # 重新打开页面，用于判断是否显示二维码
                    # 管理员已设置当前用户无需进行otp验证
                # 验证通过

            else:
                error_msg = "用户名/密码错误，或用户已停用"
                raise

            # 用户登陆
            auth.login(request, user)
            # 检查密码过期
            if userprofile.chk_pwd_expired():
                r_url = '/password_change?next=%s' % r_url
            return HttpResponseRedirect(r_url)
        except Exception as e:
            print(e)
            raise
            pass

    return render(request, 'base/login.html', locals())


def logout(request):
    auth.logout(request)  # Session登出
    # import ipdb;ipdb.set_trace()
    response = HttpResponseRedirect("/login")
    return response


@login_required()
def password_change(request):
    if request.method == "POST":
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        password3 = request.POST.get("password3")
        if password2 != password3:
            error_msg = "二次密码输入不一致"
        else:
            user = request.user
            if user.check_password(password):
                user.set_password(password2)
                user.save()
                userprofile = user.profile
                userprofile.pwdtime = datetime.now()
                userprofile.save()
                ok_msg = "密码修改成功"
                # return HttpResponseRedirect(r_url)
            else:
                error_msg = "旧密码错误"

    return render(request, 'base/password.html', locals())
