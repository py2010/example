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
    priority.set_conf(__name__, re_load=True, reload_timeout=10, reload_settings=True)  # py配置修改, 免重启刷新

# --------- 配置开始 ----------

PATH = 'test'
PWD = {1: 1}  # 当env_convert=True, 而环境变量不支持配置字典, 虽优先但会忽略
STATIC_URL = 333

# c/d s  # 进入django shell

'''
In [1]: from config import conf_example

In [2]: conf_example.PATH
Out[2]: '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/bin'

In [3]: conf_example.PWD
Out[3]: {1: 1}  # env_convert is True and dict not in priority.ENV_DATA_TYPES

In [4]: conf_example.STATIC_URL
Out[4]: '/static/'

'''

# c/d s

# from config import confile
# yml = confile.YML('docker-compose.yml')  # ***/project/docker-compose.yml
# locals().update(yml)  # 将YML配置加载到当前conf
# print(services, 111)

# yml._deep_update_({'services': {'test': {1: 2}}})
# print(yml.services, 222)

# # DEBUG
# import ipdb; ipdb.set_trace()  # breakpoint 7e9cd84c //

