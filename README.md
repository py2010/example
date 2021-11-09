# django-views-templates 示例

django-low-code 低代码演示, 项目 https://github.com/py2010/django-generic-views-templates

* 功能:

        django通用视图/模板演示
        示例模板使用的 inspinia_admin-v2.7 大家可自行换成自己的模板.
        1. 通用视图模板
        2. 列表页分页/查询/SQL优化
        3. 虚拟关联
        4. 可使用自动路由, urls/views/templates全自动处理

* app:

        apps/generic/  # django-views-templates项目APP
        apps/a/  # 常规功能演示 (数据库: default)
        apps/mirror/  # 零代码演示, 全自动生成 http://127.0.0.1:808/mirror/各models页-增删改查/
        apps/vr/  # 跨库外键/m2m演示 (数据库: vr)


* 环境：

        linux (目录c中的脚本为.sh, 如果是windows需手工runserver)
        python3.6 (字符串基本是使用f'{var}')
        django2.2 (django 1.11估计也支持, 没详细测试)

* 部署：

        # python3, 安装依赖库:
        pip3 install django==2.2.20
        pip3 install PyYAML==5.1
        pip3 install django-bootstrap3==11.1.0

        # 拉取代码
        git clone https://github.com/py2010/example
        或国内 git clone https://gitee.com/py2010/example

        # 运行django - runserver
        cd example
        c/d

        # 访问网站
        http://127.0.0.1:808
        使用账号/密码都是"demo"进行登录


* 常规功能演示图
![a](a.png  "常规")


* 跨库关联 - 演示图
![vr](vr.png  "跨库")


* 其它的大家自己研究.

        所有演示功能对应的主体程序都在 apps/generic/ 目录,
        项目中有很多文件夹是从以前其它项目中复制的, 所以有很多没用的文件懒得整理了,
        多出的文件不影响演示.

