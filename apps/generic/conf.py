# -*- coding: utf-8 -*-
try:
    from config import priority
except ImportError:
    pass
else:
    '''
    根据优先级, 更新各app/conf.py中的配置项的值.
    使各app业务程序只管从各自的conf.py取配置, 而无需关注比如优先从环境变量取.

    优级级取值的配置项不能含有小写字母, 否则忽略优先级处理.
    未指定优先级时, priority_confs 使用默认值 ['env', 'settings', 'conf']
    默认优先级: env环境变量 > project.setting / YML > app.conf

    环境变量值只支持字符串, 默认会进行转换成配置项原值的类型, 使类型保持一致.
    (字符串)列表字典等转换时, 默认为json.loads(), 要自定义处理或为特殊类,
    请增加自定义方法: priority.EnvConvert.xx类名() 函数进行处理.

    示例:
    priority.set_conf(__name__, priority_confs=['env', 'conf'], env_convert=False)  # env_convert不转换环境变量
    '''
    priority.set_conf(__name__, re_load=True, reload_settings=True)  # py配置修改, 免重启刷新

# --------- 配置开始 ----------

EMPTY_VALUE_DISPLAY = '-'  # 表格表单数据为空时(None), 显示字符

# 列表页通用视图, 相关参数宏观配置

LISTVIEW_FILTER_ORM_FIELDS = []  # 开启ORM过滤的字段，列表或'__all__'.
# LISTVIEW_FILTER_ORM_FIELDS = '__all__'  # 小心CC
LISTVIEW_FILTER_ORM_PREFIX = ''  # ORM过滤字段参数增加前缀，以免出现参数混淆，比如字段名为page

LISTVIEW_PAGE_KWARG = 'page'  # url页码名称, &page=3
LISTVIEW_PAGE_SIZE = 20  # 每页条数
LISTVIEW_PAGE_SIZE_KWARG = 'pagesize'  # 每页条数-url变量名称, &pagesize=20
LISTVIEW_PAGE_SIZE_LIST = [
    20, 30, 50,
]  # 页面PageSize选择列表, 供用户动态改变每页显示条数.


'''
MyRouter自动url, 相关参数宏观配置
action:value字典key的{action}为标识名, 相当于不可修改的变量名, {value}为配置值
'''

ROUTER_ACTIONS = {
    # 增删改查, 哪些action类型的url需自动生成, 未配置则为None
    # {action}: {value}
    # True: 生成
    # False: 不生成
    # None: 默认
    'create': None,
    'delete': None,
    'update': None,
    'detail': None,
    # 'list': False,  # ListView.list_fields 为空时, 只显示一列object_list
}

ROUTER_URL_RULES = {
    # 配置各action页面的URL路径规则, 用于自动生成urls
    # .../app_label/model_name/{action_url_rule}
    # {action}: {action_url_rule}, 比如admin_urls规则:
    # 'create': r'add/$',
    # 'update': r'(?P<pk>\d+)/change/$',

    'create': r'create/$',
    'delete': r'delete/$',
    'update': r'(?P<pk>\d+)/update/$',
    'detail': r'(?P<pk>\d+)/$',  # model_name根路径+主键ID, 打开Detail页
    'list': r'$',  # 访问model_name根路径, 打开列表页

}


