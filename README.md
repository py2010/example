# django-views-templates 示例

django-low-code 低代码演示, 项目 https://github.com/py2010/django-generic-views-templates

* 功能:

        django通用视图/模板演示
        示例模板使用的 inspinia_admin-v2.7 大家可自行换成自己的模板.
        1. 通用视图模板
        2. 列表页分页/查询/SQL优化
        3. 虚拟关联

* app:

        apps/generic/  # django-views-templates项目APP
        apps/a/  # 常规功能演示 (数据库: default)
        apps/mirror/  # a的镜像, 零代码演示
        apps/vr/  # 跨库外键/m2m演示 (数据库: vr)


* 环境：

        linux
        python3.6
        django2.2 (django 1.11可能也支持)

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


* 跨库关联 - 演示图
![vr](vr.png  "跨库")


* 其它的大家自己研究.


