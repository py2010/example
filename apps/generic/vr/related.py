# coding=utf-8

from django.db.models.fields import related as _dj
from . import related_descriptors
# from . import reverse_related


class ForeignKey(_dj.ForeignKey):

    column_field = None  # VirtualRelation配置的外键字段--对应在model中的真实字段, column数据库字段需一致.
    # rel_class = reverse_related.ManyToOneRel

    # def get_cache_name(self):
    #     # 为了防止虚拟字段刚好和model本身字段重名, 虚拟关联字段加~
    #     cache_name = super().get_cache_name()
    #     return f'~{cache_name}'

    def _check_column_field(self):
        # 检查表字段 db_column 是否存在, 或对应的model虚拟外键字段是否存在
        for name, field in self.model._meta._forward_fields_map.items():
            if self.column == field.column:
                self.column_field = field
                self.attname = field.attname  # django2.* getattr(vr, vr_field_id) 返回 vr._model_instance.field_id
                return True
        if not self.column_field:
            # 虚拟外键关联需有真实数据基础, 当前字段db_column配置错误, 或模型中不存在db_column一致的普通字段
            print(
                f'\n\n\nError: 模型{self.model}虚拟关联字段{self.name}配置错误,\n'
                f'model数据库表不存在字段{self.column}, 或者这个表字段没有对应的model字段'
            )

    def get_attname(self):
        # django1.* 有时使用self.attname有时使用self.get_attname()
        if self.column_field:
            return self.column_field.attname  # getattr(vr, vr_field_id) 返回 vr._model_instance.field_id
        return '%s_id' % self.name

    def contribute_to_class(self, vr, name, **kwargs):
        # field 转 field_descriptor
        self.set_attributes_from_name(name)
        self.model = vr._model
        if self._check_column_field():
            vr._fields[name] = self

            if not vr._model._meta.abstract:
                def resolve_related_class(model, related_model, field):
                    field.remote_field.model = related_model
                    field.do_related_class(related_model, model)
                # 关联模型可能未初始化注册(使用字符串), 比如 ForeignKey(to='app_lable:model_name'), 需延迟到对方注册时处理.
                _dj.lazy_related_operation(resolve_related_class, vr._model, self.remote_field.model, field=self)

            descriptor = getattr(related_descriptors, self.forward_related_accessor_class.__name__)(self)
            setattr(vr, name, descriptor)

    # def do_related_class(self, other, cls):
    #     self.set_attributes_from_rel()
    #     self.contribute_to_related_class(other, self.remote_field)

    def contribute_to_related_class(self, cls, related_field):
        # super().contribute_to_related_class(cls, related_field)
        if not self.remote_field.is_hidden() and not related_field.related_model._meta.swapped:
            model = cls._meta.concrete_model
            vr = getattr(model, 'VirtualRelation', None)
            if not vr:
                from .models import VR

                class VirtualRelation(VR):
                    1
                temp = VirtualRelation  # VirtualRelation已转为实例
                temp.contribute_to_class(model)
                vr = temp.vr

            vr._fields[related_field.get_accessor_name()] = related_field
            rel_descriptor = getattr(related_descriptors, self.related_accessor_class.__name__)(related_field)
            setattr(vr, related_field.get_accessor_name(), rel_descriptor)

        if self.remote_field.field_name is None:
            self.remote_field.field_name = cls._meta.pk.name


class OneToOneField(_dj.OneToOneField, ForeignKey):
    '''正向o2o'''
    # rel_class = reverse_related.OneToOneRel


class ManyToManyField(_dj.ManyToManyField):
    '''
    m2m虚拟关联配置时, 必须提供through=中间表.
    m2m = o2m + m2o
    多对多可通过 (反向外键 --> 中间表 --> 正向外键) 来实现, 在中间表配置两个虚拟外键关联.
    '''
    '略, 由于虚拟关联必需有中间表, 虚拟m2m意义不大, 请通过配置o2m + m2o两次虚拟关联实现.'
    '这不同于django官方的多对多真实关联, 除非中间表需增加自定义字段外, 通常不需要配置through,'
    '由程序自动创建中间表, 简化用户使用, 所以真实m2m有它的意义之处. 而虚拟m2m无此必要.'

