# -*- coding: utf-8 -*-
# exia@qq.com
import os
import sys
import json
import time
# import traceback
import logging
import weakref
from django.conf import settings, ENVIRONMENT_VARIABLE

from .reloader import ReLoader

reloader = ReLoader()
settings_name = os.environ.get(ENVIRONMENT_VARIABLE)
settings_module = sys.modules[settings_name]  # project.settings

logger = logging.getLogger()

'''
根据优先级, 更新各app.conf中的配置项的值.
使各app业务程序只管从各自的conf.py取配置, 而无需关注比如优先从环境变量取.
优先级由conf.py中set_conf()参数指定, 未指定则使用默认优先级.

优级级取值, 只支持全为大写的attr配置项, 如果含小写字母则不作处理, 为conf本身取值.
由于环境变量只支持字符串值, 会自动根据需要转为(str, int, float, bool, ...)类型,

python3.6 开发/测试
'''

# 默认优先级: 环境变量 > setting / YML > app.conf
DEFAULT_PRIORITY = [
    'env',  # 环境变量
    'settings',  # django.conf.settings / YML
    'conf',  # app.conf
]

# 环境变量值, 支持类型. (不支持的类型, env_convert=True时即使环境变量优先, 也会被忽略)
# 如果要增加其它类型支持, 请自定义EnvConvert对应函数功能, 比如dict为EnvConvert.dict()
ENV_DATA_TYPES = [
    str, int, float, bool,
    tuple,
    list,
    dict,
]


class EnvConvert:
    '''环境变量值只支持字符串, 自动转换类型'''

    types = ENV_DATA_TYPES

    def __call__(self, env_data, ref_data):
        data_type = type(ref_data)  # 参考值类型
        if data_type not in self.types:
            # 不在ENV_DATA_TYPES列表, 比如dict, py对象等..., 直接使用参考值, 高优先级的环境变量中的配置会被忽略!!
            return ref_data
        func = getattr(self, data_type.__name__, data_type)
        try:
            return func(env_data)  # 转换
        except Exception:
            # 类型转换出错, 返回字符串原值
            return env_data

    def bool(self, env_data):
        if env_data.lower() in ('0', 'false', 'none', 'null'):
            return False
        return bool(env_data)

    def dict(self, env_data):
        # 环境变量字典类型的值, 格式为json.dumps处理后的格式
        return json.loads(env_data)

    # def list(self, env_data):
    #     # 环境变量列表类型的值, 格式为"值1,值2,值3..."
    #     return env_data.split(',')

    list = dict
    tuple = list


convert = EnvConvert()
CACHE_ATTR = '_cache_datas'  # 保存缓存
CACHE_CLEAR_ATTR = '_cache_clear_time'  # 保存上次清空缓存时间

conf_proxys = {
    # module_name: conf_proxy,
}


def get_proxy(name):
    if name in conf_proxys:
        # 重载conf时
        proxy = conf_proxys[name]
    else:
        # 程序启动时, 首次加载
        proxy = ConfProxy(name)
        conf_proxys[name] = proxy
    return proxy


class ConfValue:
    attr = None  # 配置名称
    kind = None  # 配置类型
    value = None  # 配置值
    error = None  # 取值出错
    has_val = False  # 是否有配置值

    def __repr__(self):
        return f'{self.attr} <kind: {self.kind}, value: {self.value}>'

    def __bool__(self):
        return self.has_val

    def __setattr__(self, attr, val):
        if attr == 'value':
            # 因配置值本身有可能为(False, None...), 所以使用has_val表示__bool__
            self.has_val = True  # 有配置值
        return super().__setattr__(attr, val)

    def __init__(self, attr, kind=None, conf_module=None):
        self.conf_module = conf_module
        self.attr = attr
        if kind:
            self.kind = kind
            try:
                getattr(self, f'from_{kind}')()
            except Exception as e:
                self.error = e

    def from_env(self):
        if self.attr.isupper():
            self.value = os.environ[self.attr]
        raise KeyError  # 含小写字母则忽略环境变量

    def from_settings(self):
        self.value = getattr(settings, self.attr)

    def from_conf(self):
        if self.conf_module:
            self.value = getattr(self.conf_module, self.attr)


class ConfProxy:
    '''ConfObject 的代理'''

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.conf_module.__name__}'>"

    __str__ = __repr__

    def __init__(self, conf_module_name):
        self.conf_module = sys.modules[conf_module_name]
        self.conf_module._proxy = weakref.proxy(self)

        setattr(self, CACHE_ATTR, {})  # 设置属性 - 缓存
        setattr(self, CACHE_CLEAR_ATTR, time.time())  # 设置属性 - 过期时间

        self.FIRST = True  # 区分首次load还是reload, 首次时需替换系统模块

    # def __getattr__(self, attr):
    #     return getattr(self.conf_module, attr)

    def check_reload(self, now_time=time.time()):
        # 检查配置文件, 有修改则重载
        if self.re_load:
            RELOADED = reloader.check_module(self.conf_module, self.reload_timeout, now_time)  # conf.py是否已重载
            if self.reload_settings and 'settings' in self.priority_confs:
                # 检查settings是否修改
                if reloader.check_module(settings_module, self.reload_timeout, now_time):
                    # project.settings已重载, 更新 django.conf.settings
                    RELOADED = True
                    settings._setup()
            return RELOADED

    def check_cache(self, now_time=time.time()):
        # 缓存是否过期
        return now_time - getattr(self, CACHE_CLEAR_ATTR) > self.cache_timeout

    def get_cache(self):
        # 检查后返回缓存数据, 检查内容, 1.重载配置, 2.缓存过期
        cache_datas, now_time = {}, time.time()
        RELOADED = self.check_reload(now_time)

        if self.cache:
            cache_datas = getattr(self, CACHE_ATTR)
            if RELOADED or self.check_cache(now_time):
                setattr(self, CACHE_CLEAR_ATTR, now_time)
                logger.debug(f'清空配置缓存: {self.conf_module_name}')
                cache_datas.clear()  # 清空缓存
        return cache_datas

    def get(self, attr):
        '''
        ConfObject --> ConfProxy --> env/settings/conf
        根据优先级顺序, 进行取值.
        比如: 取 app.conf.attr 配置时, 优先从环境变量取值,
        其次取 settings.attr, 最后取 app.conf.attr
        只有高优先级的配置不存在时, 低优先级的才生效.
        '''
        # print(attr, 11111111)
        cache_datas = self.get_cache()
        if attr in cache_datas:
            # 从缓存中取
            return cache_datas[attr]

        result = ConfValue(attr)
        for kind in self.priority_confs:
            val = ConfValue(attr, kind, self.conf_module)
            if val:
                if result:
                    # env_convert为True, 上次取得的环境变量字符串值, 需根据参考值还原类型.
                    result.value = convert(result.value, val.value)
                    break

                else:
                    if self.env_convert and kind == 'env':
                        # 环境变量值都是字符串, 需还原类型, 会继续循环取参考值.
                        result.kind = kind
                        result.value = val.value
                    else:
                        # 按优先级, 成功取得配置值
                        # print(val.value, 3333333)
                        result.value = val.value
                        break
            else:
                if not result:
                    result.error = val.error

        if result:
            if self.cache and attr != CACHE_ATTR:
                # 缓存数据, 以便后续直接从缓存取值
                cache_datas[attr] = result.value
            return result.value
        else:
            raise result.error

    def set(self, attr, val):
        # (大写字母)配置项禁止业务程序setattr
        raise UserWarning(
            '不建议将业务数据保存到配置项中, 因为不同于conf文件模块的静态配置值, 当前取值是动态的,'
            '所以可能会与优先级取值/配置重载等功能冲突, 导致setattr值被刷新或删除.'
        )
        # if not self.re_load:
        #     return setattr(self.conf_module, attr, val)

    def update_func_kwargs(self):
        '''
        reload时, 当conf.py修改了set_conf()参数后, 免重启刷新最新的set_conf()参数.
        由于各应用程序中的conf引用, 是在程序启动时就固定了, 通常不会再重新引入配置模块,
        所以ConfObject一直是首次的旧实例, reload时不再实例化, 当conf修改了set_conf参数时,
        为了实现reload不仅能刷新业务配置, 同时也能更新set_conf参数, 比如reload_settings调整.
        所以保存最新参数, 以实现免重启刷新最新set_conf()参数修改.

        注意: re_load=True时, conf.py后续改成False, 新参数会生效 -- 会关闭reload功能,
             因重载功能已关闭, 后续re_load再改为True时, 不会再触发更新业务配置和set_conf参数,
             此时新配置只有重启程序才会生效.
        '''
        func = sys._getframe().f_back  # set_conf()
        code = func.f_code
        n = code.co_argcount  # set_conf()参数个数
        if code.co_flags & 0b100:
            n += 1  # 函数带 *args
        if code.co_flags & 0b1000:
            n += 1  # 函数带 **kwargs

        for i in range(n):
            name = code.co_varnames[i]
            val = func.f_locals[name]
            logger.debug('priority.set_conf()当前最新参数: %s = %r' % (name, val))
            setattr(self, name, val)


def set_conf(conf_module_name,
             priority_confs=DEFAULT_PRIORITY,
             env_convert=True,
             cache=True,
             cache_timeout=300,  # 秒数(int)
             re_load=False,
             reload_timeout=300,  # 秒数(int)
             reload_settings=False,
             ):
    '''
    用于各app.conf根据配置优先级, 设置使用对应配置值
    参数说明:
        conf_module_name: app.conf模块名__name__,
        priority_confs: 优先级/配置类型列表,
        env_convert: 环境变量值-是否自动转换. (字符串转为 ENV_DATA_TYPES 中的类型)
                 因环境变量的值只支持字符串, 当优先使用环境变量时, 是否自动转换为正确类型
        cache: 是否缓存配置
                False: 每次取值时都会按优先级处理进行取值,
                       比如优先取环境变量, 有更新时会实时取到环境变量新值.
                       但py配置有更新, 并不会更新, 需重启程序或开启reload.
                True:  开启缓存以免重复处理, 缓存会定期(cache_timeout)刷新.
                       首次取值时, 会按优先级处理, 之后在缓存过期前使用缓存,
                       比如优先取环境变量, 只支持环境变量定期刷新.
        cache_timeout: 缓存过期时间, 过期后清空缓存, cache=True 才有效.
        re_load: 发现配置文件有修改, 是否重载. 使py等配置更新后不用重启程序.
                False: 不重新加载配置, 配置文件有修改, 只有重启才生效.
                True:  定期检查, 若配置文件有修改, 自动重新加载py更新配置, 并清空缓存.
        reload_timeout: 重载配置过期时间, 定期检查重载配置, re_load=True 才有效.
        reload_settings: 重载检查, 是否也包含settings.py配置,
                         开启后若settings有修改, 定期检查时会自动重载.
                         re_load=True 且 'settings' in priority_confs 才有效.
                False: 只监视conf.py, 有修改则重载conf模块.
                True: 监视conf.py, settings.py conf.yml 任何配置有修改, 定期都自动重载模块.

    使用注意:
        开启reload功能时, 由于配置值可能更新, 应用程序使用配置时应当直接从conf取值, 而不是定义新变量引用,
        比如 val = conf.VAL, 当 conf.VAL 值修改并reload, 此时val仍指向旧值, 因此应当直接使用conf.VAL

    配置示例:
        # app/conf.py
        from config import priority
        priority.set_conf(__name__, priority_confs=['env', 'conf'], re_load=True)
        ...配置项
        ...配置项
    '''

    proxy = get_proxy(conf_module_name)
    proxy.update_func_kwargs()  # 每次reload时都应处理, 保存当前最新参数

    class ConfObject:
        '''
        conf.py文件模块转py对象, 以支持__getattribute__, 实现自定义控制取值.
        '''

        def __repr__(self):
            return proxy.conf_module.__repr__().replace('<module ', '<ConfObject ')

        __str__ = __repr__

        def __getattribute__(self, attr):
            if attr.isupper():
                return proxy.get(attr)
            else:
                return getattr(proxy.conf_module, attr)
            # return super().__getattribute__(attr)  # self.conf_module

        def __setattr__(self, attr, val):
            if attr.isupper():
                return proxy.set(attr, val)
            else:
                return setattr(proxy.conf_module, attr, val)

    if proxy.FIRST:
        '''
        当启动程序, 首次加载时
        sys.modules替换conf.py模块为conf_object实例, 实现按优先级取值的功能.
        由于各应用程序中的conf导入, 是在程序启动时就固定了, 通常不再重新引入配置模块,
        所以以后每次reload只更新配置, sys.modules必须是首次的实例, 不重新生成新实例.
        '''
        sys.modules[conf_module_name] = ConfObject()  # 替换模块
        proxy.FIRST = False

        if re_load:
            # conf加入监视, 用于reload时检查配置文件是否有修改
            reloader.add_watch(proxy.conf_module)
            # if reload_settings and 'settings' in priority_confs:
            # 不管有没开启reload_settings, 必需保存首次加载时settings文件时间, 以支持后续调整set_conf()参数
            reloader.add_watch_settings(settings_module)


# def __getattr__(attr):
#     '''
#     conf.attr 不存在时, 从环境变量取值,
#     py版本最低要求python3.7 (PEP 562)
#     不支持__getattribute__, 也就是不支持环境变量优先于 conf.attr.
#     '''
#     # print(attr, 111111)
#     try:
#         return os.environ[attr.upper()]
#     except KeyError:
#         raise AttributeError
