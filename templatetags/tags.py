# coding=utf-8
# from importlib import import_module
from allapp import URLS_APPS, settings
import os
from collections import OrderedDict

from django.utils.html import format_html
from django.urls import reverse
from django.core.cache import cache
import logging
from django import template
register = template.Library()
logger = logging.getLogger()

# 菜单配置
MENUS = []  # 自定义增加
APP_MENU_HTML_TIMEOUT = 600  # 增删html菜单文件时,缓存超时时间, 单位秒


@register.filter
def debug(mm, nn=None):
    # 自定义过滤器 - 模板调试 {{ mm|debug:nn }}
    print({'mm': mm, 'nn': nn})
    import ipdb; ipdb.set_trace()
    return


@register.simple_tag
def add(*args):
    # 自定义标签 -- 字符串拼接 {% add a b c %} (内置过滤器add一次只能拼接二个变量, 语法长不直观)
    return ''.join([str(i) for i in args])


@register.simple_tag(takes_context=True)
def load_menus(context, *args, **kwargs):
    # 用于生成左边栏菜单
    # import ipdb; ipdb.set_trace()

    appmenus = cache.get('app_menus', OrderedDict())  # 含有左边栏的app/_menu.html列表
    # redis支持OrderedDict存取, 无需转换

    if not appmenus:

        # 开始生成左边栏菜单
        for app in URLS_APPS:
            html_name = f'{app}/_menu.html'
            html_file = os.path.join(settings.BASE_DIR, 'apps', app, 'templates', html_name)
            logger.info(html_file)
            if os.path.isfile(html_file):
                # app含有左边栏菜单
                # 开始检查app是一级菜单还是二级菜单
                menu_level = 1
                menu_name = app  # 一级菜单名
                if app in MENUS:
                    menu_level = 2
                    menu_name = MENUS[app]  # 一级菜单名

                key = (menu_level, menu_name)
                if key in appmenus:
                    # 通常为2级菜单
                    appmenus[key].append(html_name)
                else:
                    # 1级菜单
                    appmenus[key] = [html_name, ]
                # appmenus.append(html_name)
        cache.set('app_menus', appmenus, APP_MENU_HTML_TIMEOUT)

    # import ipdb;ipdb.set_trace()
    return appmenus


@register.simple_tag(takes_context=True)
def show_menu_url(context, name, viewname, *perms):
    '''
    根据用户权限返回某项菜单的网址, 用于模板判断是否在左边栏显示菜单
    {% show_menu_url '网址视图' '权限码1' 'and' '权限码2' as url_xx项 %}
    多个权限未提供逻辑与或时, 默认为or, 也就是'or' 可以省略.
    '''
    user = context['request'].user
    if user.is_superuser:
        show_menu = True
    else:
        show_menu = False
        for n, perm in enumerate(perms):
            if perm not in ('and', 'or'):
                logic = perms[n - 1]
                if logic == 'and':
                    show_menu &= user.has_perm(perm)
                else:
                    show_menu |= user.has_perm(perm)

    if show_menu:
        try:
            return format_html(f'<a href={reverse(viewname)}>{name}</a>')
        except Exception:
            pass
    return ''


@register.tag('ifmenu')
def do_ifmenu(parser, token):
    '''
    使用分布式菜单 app/templates/app/_menu.html 时，
    用于控制是否显示母菜单，但又无需设置布尔表达式，以简化配置。
    通常情况下，当有某个子菜单权限时，则上级母菜单应当也有权限，
    因此根据子菜单 show_menu_url 权限，自动按需显示/隐藏母菜单。
    使用示例：
    {% ifmenu %}
        <li>
            <a><i class="fa fa-book"></i> <span class="nav-label">母菜单</span>
                <span  class="fa arrow"> </span></a>
            <ul class="nav nav-second-level">
                <li>{% show_menu_url '子菜单1' 视图url1 权限1 and 权限2 %}</li>
                <li>{% show_menu_url '子菜单2' 视图url2 权限3 or  权限4 %}</li>
            </ul>
        </li>
    {% else %}
        <!-- 没有<子菜单1><子菜单2>..权限时显示... -->
    {% endifmenu %}

    用于取代if类似功能：{% if (权限1 and 权限2) or (权限3 or 权限4) %} ...
    尤其子菜单多时，分布式菜单中使用if会产生大量冗余重复配置，后续增减子项维护麻烦，
    而改用集中式菜单，过于抽象使用起来不直观，且代码通用性差，在大系统中还会增加协调成本。
    '''
    bits = token.split_contents()[1:]
    if_nodelist = parser.parse(('else', 'endifmenu'))
    token = parser.next_token()

    # {% else %} (optional)
    if token.contents == 'else':
        else_nodelist = parser.parse(('endifmenu',))
        token = parser.next_token()
    else:
        else_nodelist = None

    # {% endifmenu %}
    if token.contents != 'endifmenu':
        raise template.base.TemplateSyntaxError(
            'Malformed template tag at line {0}: "{1}"'.format(token.lineno, token.contents))

    return IfMenuNode(if_nodelist, else_nodelist)


class IfMenuNode(template.base.Node):

    def __init__(self, if_nodelist, else_nodelist):
        self.if_nodelist, self.else_nodelist = if_nodelist, else_nodelist

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def render(self, context):
        # 有任何子菜单权限 (show_menu_url非空)，将显示上级母菜单。
        match = False
        # self.if_nodelist.render(context)
        bits = []
        for node in self.if_nodelist:
            if isinstance(node, template.base.Node):
                bit = node.render_annotated(context)
                if not match and getattr(node, 'func', None) is show_menu_url:
                    if bit:
                        # show_menu_url 子菜单有生成链接，表示有子菜单权限
                        match = True
            else:
                bit = node
            bits.append(str(bit))
        resp = template.base.mark_safe(''.join(bits))

        if match:
            return resp

        elif self.else_nodelist:
            # {% else %} ..... {% endifmenu %}
            return self.else_nodelist.render(context)

        return ''

