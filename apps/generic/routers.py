# coding=utf-8

import sys
import logging
from importlib import import_module
try:
    from django.urls import re_path
except Exception:
    from django.conf.urls import url as re_path  # django 1.*

from . import views
from . import conf

logger = logging.getLogger()


class MyRouter:
    """根据Model, 自动生成对应的Views和urls"""
    INDEXS = {
        5: 'create',
        4: 'delete',
        3: 'update',
        2: 'detail',
        1: 'list',
    }

    def __init__(self, model, args=0b11111, **kwargs):
        '''
        model 用户提供的模型对象, 用于自动生成对应的ModelView
        args 和 kwargs, conf.ROUTER_ACTIONS 都是用来确定生成哪些view,
        配置冲突时, 配置优先级:
        kwargs 自定义配置 > 宏观配置(conf.ROUTER_ACTIONS ) > args

        kwargs: action字典, 比如(create=True, list=False)表示生成CreateView, 不生成ListView,
            action字典会合并宏观配置 conf.ROUTER_ACTIONS, 当某项action为None时, 则由args参数确定.
            True: 生成
            False: 不生成
            None: 由args确定

        args: 只对action字典中未配置的action才生效,
            五位二进制数字, 1为开启, 0为禁用
            分别代表是否开启生成 "增/删/改/查单/查列" 对应的View和url,
            5: create
            4: delete
            3: update
            2: detail
            1: list
            默认0b11111表示所有action都自动生成,
            比如 0b00011, 表示增删改的视图和url由人工定义,
            只自动生成 DetailView ListView 视图及对应url

        '''
        self.model = model
        self.args = args
        self.set_actions(kwargs)  # 合并args配置

        self.urls = []
        self.app_views = None
        self.done = False

    def __getitem__(self, i):
        if not self.done:
            self.done = True
            self.set_app_views()
            self.set_urls()
        return self.urls[i]

    def set_app_views(self, app_views=None):
        # 绑定 app.views 模块，以备后用。
        # 自动路由时，优先利用视图模块中人工开发的同名视图，
        # 当同名视图不存在时才会自动生成 ModelActionView
        if not self.app_views:
            if app_views:
                self.app_views = app_views
            else:
                try:
                    urls_locals = sys._getframe().f_back.f_back.f_locals
                    self.app_views = get_module(urls_locals, 'views')
                except Exception:
                    logger.info(
                        f"""无法获取视图模块({self.model._meta.app_label}.views)，
                        当前模型({self.model.__module__}.{self.model.__name__})将无法利用人工编写的ModelView(若有)
                        来自动生成路由，所需视图将和路由一样都将自动生成"""
                    )

    def set_actions(self, kwargs):
        self.actions = conf.ROUTER_ACTIONS.copy()  # 默认actions配置
        self.actions.update(kwargs)  # 加载urls.py提供的actions
        for index in range(1, 6):
            self.set_action(index)
        logger.debug(f'{self.actions} - ({self.model._meta.app_label}.{self.model.__name__})')

    def set_action(self, index):
        if index in self.INDEXS:
            action = self.INDEXS[index]
            if self.actions.get(action) is None:
                # actions中未配置时, 根据args来确定是否生成action对应的视图和url
                enable = self.args & (1 << (index - 1)) > 0
                self.actions[action] = enable

    def set_urls(self):
        for action, enable in self.actions.items():
            if enable:
                self.urls.append(self.get_url(action))

    def get_url(self, action):
        # 自动创建url路由
        model_name = self.model._meta.model_name
        url_path = self.get_url_path(action)
        return re_path(
            rf'^{model_name}/{url_path}',
            self.get_view(action).as_view(),
            name=f"{model_name}_{action}"
        )

    def get_url_path(self, action):
        # url路由对应的路径
        return conf.ROUTER_URL_RULES.get(action, f'{action}/')

    def get_view(self, action):
        view_name = f'{self.model.__name__}{action.capitalize()}View'
        view = getattr(self.app_views, view_name, None)

        if not view:
            kwargs = {
                '__module__': f'{__name__}.{self.model._meta.app_label}',
                'model': self.model,
            }
            if action in ['create', 'update']:
                kwargs['fields'] = '__all__'

            view =  type(
                # 自动创建MyModelView视图, 用于urls.py调用
                view_name,
                (getattr(views, f'My{action.capitalize()}View'), ),
                kwargs
            )
            logger.info(f"使用模型 {self.model.__module__}.{self.model.__name__} 创建视图: {view_name}")
            if self.app_views:
                setattr(self.app_views, view_name, view)
                logger.debug(f"在 {self.app_views.__name__} 中加入新视图: {view_name}")

        return view


    @classmethod
    def add_router_for_all_models(cls, urlpatterns=None, models=None, views=None, args=0b11111, **kwargs):
        # 自动为models模块中所有的模型创建urls/views.
        urls_locals = sys._getframe().f_back.f_locals
        urlpatterns = urlpatterns or urls_locals['urlpatterns']  # 未提供则自动从urls.loacls()中取
        models = models or get_module(urls_locals, 'models')
        app_views = views or get_module(urls_locals, 'views')

        logger.debug(f"{urls_locals.get('__name__')} 自动路由...")
        for attr in dir(models):
            if attr.startswith('_'):
                continue
            model = getattr(models, attr)
            if hasattr(model, '_meta') and not model._meta.abstract:
                # 根据模型自动生成url路由
                router = MyRouter(model, args, **kwargs)
                router.set_app_views(app_views)  # f_back数一致，需在此触发set_app_views(None)
                urlpatterns.extend(router)


def get_module(urls_locals, module_name):
    # 未提供models/views时, 自动从urls模块所在基目录加载
    module = urls_locals.get('module_name')
    if module:
        return module
    module_path = urls_locals['__name__'].split('.')[:-1]
    module_path.append(module_name)
    return import_module('.'.join(module_path))


'''
自动生成url及视图, 使用方法:


# urls.py

from generic.routers import MyRouter
from . import models  # 用于自动views
from . import views  # 用于人工views，或自动路由使用已有的 ModelActionView

urlpatterns = [

    # 所有urls及视图都自动创建 (默认配置conf.ROUTER_ACTIONS={})
    *MyRouter(models.Xxx),


    # 如果需使用自定义配置的人工ListView, 除此之外其它自动生成, 则:
    *MyRouter(models.Xxx, list=False),
    re_path(r'^xxx/$', views.XxxListView.as_view(), name='xxx_list'),


    # 如果 增删改 人工配置, 其它自动生成, 则:
    re_path(r'^xxx/create/$', views.XxxCreateView.as_view(), name='xxx_create'),
    re_path(r'^xxx/delete/$', views.XxxDeleteView.as_view(), name='xxx_delete'),

    re_path(r'^xxx/(?P<pk>\d+)/update/$', views.XxxUpdateView.as_view(), name='xxx_update'),

    *MyRouter(models.Xxx, 0b11),


    # 自动生成DetailView, 其它人工配置
    *MyRouter(models.Xxx, 0, detail=True),
    ...  # 其它人工处理


]


注意!!
如果自动和人工url都存在, url重复了, 则按django原理, 前面的url优先匹配路由, 使在前面的生效,

model各页面的人工URL路径规则, 如果和当前通用视图模板URL路径规则一致时(conf.ROUTER_URL_RULES),
可以将自动MyRouter()放后面, 前面有人工自定义url则优先生效, 没有则匹配自动url


# 示例:

urlpatterns = [
    ...
]
MyRouter.add_router_for_all_models()

'''
