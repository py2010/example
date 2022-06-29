# coding=utf-8

import weakref
from django.db.models.base import ModelState
from django.core import exceptions
# from django.db import models
from . import related

"""

class Demo(models.Model):
    name = models.CharField("名称", max_length=30, default='demo')
    group = models.SmallIntegerField("组ID", db_column='group_id', db_index=True, null=True, blank=True)
    user_id = models.SmallIntegerField("用户ID", db_index=True, null=True, blank=True)
    ...

    class VirtualRelation(vr.VR):
        '''
        虚拟关联 -- 虚拟字段,
        vr_field.column = model_field.column (比如db_column参数相同)
        参数 db_column, to_field 含义同django官方字段一致,
        某些参数比如on_delete在虚拟关联中无意义(目前只用于显示列表页).
        '''
        group = vr.ForeignKey(
            Group, verbose_name="组",
            # db_column='group_id',  # 与Demo.group的db_column相同, 注意不能设置为'group'
            to_field='id',
            related_name='demo',
            on_delete=models.SET_NULL, null=True, blank=True)
        user = vr.OneToOneField(
            User, verbose_name="用户",
            # db_column='user_id',  # 与Demo.user_id的db_column相同
            to_field='id',
            related_name='demo',
            on_delete=models.SET_NULL, null=True, blank=True)

"""


class Temp:

    def __init__(self, vr):
        self.vr = vr

    def contribute_to_class(self, model, name='VirtualRelation'):
        model.VirtualRelation = self.vr
        self.vr._prepare(model)


class MetaClass(type):
    """
    将model.VirtualRelation类转换为实例,
    借签model.<attr实例>.contribute_to_class()原理, 使模型初始化时可触发vr处理
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        if bases and name == 'VirtualRelation':
            return Temp(new_class)  # 改为临时的代理实例!
        else:
            return new_class

    def _prepare(cls, model):
        # 虚拟关联 -- 初始化准备
        cls._model = model
        cls.set_fields()
        cls.rewrite_model_init()

    def set_fields(cls):
        # 正向field.contribute_to_class()
        # 为兼容(虚拟关联字段和model本身真实字段重名), 将虚拟字段设置到VirtualRelation,
        cls._fields = {}
        for name in dir(cls):
            if name.startswith('__'):
                continue
            obj = getattr(cls, name)
            if hasattr(obj, 'contribute_to_class'):
                cls.check_field(obj)
                obj.contribute_to_class(cls, name)

    def check_field(cls, field):
        if isinstance(field, related._dj.ForeignKey):
            if not isinstance(field, related.ForeignKey):
                # 复制model中的字段, 比如 models.ForeignKey(), 未改成 vr.ForeignKey()
                raise exceptions.FieldError(f'字段配置错误, 关联字段{field}不是虚拟字段?')

    def get_field(cls, name):
        try:
            return cls._fields.get(name)
        except AttributeError:
            pass

    def rewrite_model_init(cls):
        '''
        重写model.__init__, 使用模型每次实例化时, 对应实例化VirtualRelation(),
        用于 vr.field_descriptor.__get__() 时获取SQL查询缓存数据--关联model实例.

        '''
        old_init = cls._model.__init__
        if old_init.__name__ == 'new_init':
            return  # 防止重复rewrite

        def new_init(self, *args, **kwargs):
            self._vr = cls()
            self._vr._model_instance = weakref.proxy(self)
            return old_init(self, *args, **kwargs)
        cls._model.__init__ = new_init


class VR(metaclass=MetaClass):
    """
    model.VirtualRelation
    使model初始化注册时, 支持对虚拟关联初始化准备, 为避免猴子补丁改写官方程序,
    增加metaclass将类替换为实例 (__init_subclass__ 无法将类替换成其它对象)
    """
    _model = None
    _model_instance = None

    def __getattr__(self, attr):
        # 注意 VirtualRelationDescriptor 不能抛出 AttributeError 错误
        # print(attr, 111111)
        return getattr(self._model_instance, attr)

    def __init__(self):
        self._state = ModelState()  # 缓存虚拟关联对象, 类似_state.fields_cache (外键, 正反o2o)
        self._state.fields_cache = {}  # 兼容 django 1.*
        self._prefetched_objects_cache = {}  # 缓存虚拟关联对象, (反向外键, 正反m2m)

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     print(cls.__module__, cls.__qualname__, 222222)
    #     # cls.test = 111111

    # def __get__(self, instance, cls=None):
    #     # print(instance, cls, 444444444)
    #     self._model_instance = instance  # model实例, 用于后续vr.field_descriptor.__get__()
    #     return self


