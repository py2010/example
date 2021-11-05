import sys
import time
import traceback
import importlib
import logging
from pathlib import Path

logger = logging.getLogger()

CACHE_ATTR = '_cache_datas'  # 保存缓存
RELOAD_ATTR = '_last_reload_time'  # 保存上次reload检查时间

'''
py/yml文件有修改, 免重启更新配置
python3.6 开发/测试
'''


class ReLoader:
    '''免重启加载新配置'''

    def __init__(self, watch_modules={}):
        '''
        re_load=True 的模块, 加入监视名单, 保存时间以便对比
        watch_modules = {
            module_name: {
                'check_time': 上次检查时间,
                文件对象1: 文件1上次修改时间,
                文件对象2: 文件2上次修改时间,
                ...
            },
        }
        '''
        self.watch_modules = watch_modules

    def add_watch(self, module):
        # 加入监视清单
        conf_path = Path(module.__file__)
        logger.info(f'加入监视配置文件: {conf_path}')
        self.watch_modules[module.__name__] = {
            'check_time': time.time(),
            conf_path: conf_path.stat().st_mtime,
        }

    def add_watch_settings(self, module):
        # settings 加入监视清单
        if module.__name__ in self.watch_modules:
            # 其它conf有开启reload, 当时settings已加入监视
            return

        # 加入监视 settings.py
        self.add_watch(module)
        # 加入监视 conf.yml
        conf_yml = getattr(module, 'CONF_YML', None)
        if conf_yml:
            yml_path = Path(conf_yml)
            logger.info(f'监视配置文件(settings-YML): {yml_path}')
            self.watch_modules[module.__name__][yml_path] = yml_path.stat().st_mtime

    def check_module(self, module, timeout, now_time=time.time()):
        # 检查配置文件模块是否有修改, timeout为防频繁检查
        module_name = module.__name__
        if module_name in self.watch_modules:
            val = self.watch_modules[module_name]
            CHANGED = False

            if now_time - val['check_time'] > timeout:
                val['check_time'] = now_time  # 更新时间
                logger.debug(f'检查模块配置文件: {module_name}')
                for path, old_time in val.items():
                    if isinstance(path, Path):
                        new_time = path.stat().st_mtime
                        if new_time != old_time:
                            logger.warning(f'配置文件有修改: {path}')
                            CHANGED = True
                            val[path] = new_time  # 需继续检查, 若多个文件都有修改, 都需更新时间
            if CHANGED:
                return self.reload_module(module)
        else:
            self.add_watch(module)

    def reload_module(self, module):

        logger.warning(f'重载 {module} reload ...........')
        for attr in dir(module):
            # 删除旧配置, 因为当配置项减少时, reload后已删配置项仍可使用, 所以先删除.
            # if attr.isupper() and not attr.startswith('__'):
            if attr.isupper():
                delattr(module, attr)
        try:
            importlib.reload(sys.modules[module.__name__])  # 重新加载模块
        except Exception:
            traceback.print_exc()
        else:
            return True
