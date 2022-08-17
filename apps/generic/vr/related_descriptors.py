# coding=utf-8

import logging
from django import __version__
from django.db.models.query_utils import DeferredAttribute
from django.db.models.fields import related_descriptors as _dj

logger = logging.getLogger()


class FieldCacheMixin:
    """原为模型字段缓存处理功能, 因虚拟关联功能简单, 统一放到descriptor字段中处理, 且兼容django 1.* """

    def get_cache_name(self):
        raise NotImplementedError('未设置名称, 通常为字段name 或 正向字段related_name')

    def get_cached_value(self, instance):
        cache_name = self.get_cache_name()
        try:
            return instance._state.fields_cache[cache_name]
        except AttributeError:
            raise Exception('出现未知错误')
        except KeyError:
            if __version__ < '2':
                return getattr(instance, cache_name)
            logger.warning('不存在的虚拟外键数据, 或者程序异常:')
            logger.warning('目前vr功能只用于列表页, 为了SQL性能暂不支持单条vr查询! 请检查列表页vr功能异常.')
            raise
            # 返回None

    def is_cached(self, instance):
        return self.get_cache_name() in instance._state.fields_cache

    def set_cached_value(self, instance, value):
        instance._state.fields_cache[self.get_cache_name()] = value

    def delete_cached_value(self, instance):
        del instance._state.fields_cache[self.get_cache_name()]


class VirtualRelationDescriptor(FieldCacheMixin):
    '''x2o关联时, 重写 vr_field_descriptor __get__和__set__ '''

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return self.get_cached_value(instance)

    def __set__(self, instance, value):
        # 只缓存当前方向, 反方向不缓存, 因目前vr功能只用于列表页, *value._vr 不需关联当前字段对应的model实例
        return self.set_cached_value(instance, value)


class ForwardManyToOneDescriptor(VirtualRelationDescriptor, _dj.ForwardManyToOneDescriptor):
    '''正向外键'''

    def get_cache_name(self):
        return self.field.get_cache_name()


class ForwardOneToOneDescriptor(ForwardManyToOneDescriptor):
    '''正向o2o'''
    1


class ReverseOneToOneDescriptor(VirtualRelationDescriptor, _dj.ReverseOneToOneDescriptor):
    '''反向o2o'''

    def get_cache_name(self):
        return self.related.get_cache_name()

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset._add_hints(instance=instances[0])

        rel_obj_attr = self.related.field.get_local_related_value
        instance_attr = self.related.field.get_foreign_related_value
        instances_dict = {instance_attr(inst): inst for inst in instances}
        # query = {'%s__in' % self.related.field.name: instances}
        # SQL过滤查询的参数, 由obj实例改为id
        if self.related.is_hidden() or len(self.related.field.foreign_related_fields) == 1:
            query = {'%s__in' % self.related.field.column_field.attname: {instance_attr(inst)[0] for inst in instances}}
        else:
            # from/to 多字段联合索引外键等特殊情况, 未处理测试不支持
            raise
        queryset = queryset.filter(**query)

        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        for rel_obj in queryset:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            if __version__ > '2':
                self.related.field.set_cached_value(rel_obj, instance)
            else:
                1  # 反向本来就可以不联接

        if __version__ < '2':
            return queryset, rel_obj_attr, instance_attr, True, self.related.get_cache_name()
        else:
            return queryset, rel_obj_attr, instance_attr, True, self.related.get_cache_name(), False


class ReverseManyToOneDescriptor(_dj.ReverseManyToOneDescriptor):
    '''反向外键'''

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # 重写RelatedManager, SQL过滤查询的参数, 由obj实例改为id, 以便兼容虚拟关联
        rewrite_reverse_many_to_one_manager(self.related_manager_cls)

    # def get_prefetch_queryset(self, instances, queryset=None):
    #     if queryset is None:
    #         import ipdb; ipdb.set_trace()  # breakpoint 2e37aced //
    #         queryset = super().get_queryset()

    #     rel_obj_attr = self.field.get_local_related_value
    #     instance_attr = self.field.get_foreign_related_value
    #     return queryset, rel_obj_attr, instance_attr, False, self.get_cache_name(), False

    # def __get__(self, vr_instance, cls=None):
    #     # print(vr_instance, cls, 66666666)
    #     instance = vr_instance and vr_instance._model_instance
    #     if instance is None:
    #         return self

    #     db_column = self.field.column  # 虚拟 ForeignKey 的 db_column
    #     to_field = self.rel.field_name  # 虚拟 ForeignKey 的 to_field
    #     return self.rel.related_model._default_manager.filter(**{
    #         db_column: getattr(instance, to_field)
    #     })  # 反查外键为instance的related_model数据, 返回QuerySet


def rewrite_reverse_many_to_one_manager(related_manager_cls):
    '''
    django.db.models.fields.related_descriptors.create_reverse_many_to_one_manager.<locals>.RelatedManager
    根据虚拟关联功能, 在原RelatedManager基础上修改功能,
    为了不影响super层数, 导致super().get_queryset()取数据差异,
    不继承生成新类, 只替换类函数, 使代码尽量和django原有保持接近.
    '''

    # class NewRelatedManager(related_manager_cls):
    #     def __init__(self, instance):
    #         super().__init__(instance)
    #         self.core_filters = {self.field.attname: getattr(instance, self.field.remote_field.field_name)}

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = super().get_queryset()

        queryset._add_hints(instance=instances[0])
        queryset = queryset.using(queryset._db or self._db)

        rel_obj_attr = self.field.get_local_related_value
        instance_attr = self.field.get_foreign_related_value
        instances_dict = {instance_attr(inst): inst for inst in instances}
        # query = {'%s__in' % self.field.name: instances}
        # SQL过滤查询的参数, 由obj实例改为id, 以便兼容虚拟关联
        if self.field.remote_field.is_hidden() or len(self.field.foreign_related_fields) == 1:
            query = {'%s__in' % self.field.column_field.attname: {instance_attr(inst)[0] for inst in instances}}
        else:
            # from/to 多字段联合索引外键等, 特殊情况未处理测试, 不支持
            raise
        queryset = queryset.filter(**query)

        # Since we just bypassed this class' get_queryset(), we must manage
        # the reverse relation manually.
        for rel_obj in queryset:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            setattr(rel_obj._vr, self.field.name, instance._model_instance)  # 反方向也可以缓存 (当前列表页功能实际用不上)
        cache_name = self.field.remote_field.get_cache_name() if __version__ > '2' else self.field.related_query_name()

        if __version__ < '2':
            return queryset, rel_obj_attr, instance_attr, False, cache_name
        else:
            return queryset, rel_obj_attr, instance_attr, False, cache_name, False

    old_init = related_manager_cls.__init__

    def new_init(self, instance):
        old_init(self, instance)
        # SQL过滤查询的参数, 由obj实例改为id, 以便兼容虚拟关联
        self.core_filters = {self.field.attname: getattr(instance, self.field.remote_field.field_name)}

    related_manager_cls.__init__ = new_init
    related_manager_cls.get_prefetch_queryset = get_prefetch_queryset


class AttNameField(DeferredAttribute):
    '''
    用于 getattr(vr, vr_field_id) 取虚拟关联字段数据库值, 返回 vr._model_instance.field_id
    '''

    def __init__(self, field_name, model=None):  # 兼容django 1.*, 多了model参数
        self.field_name = field_name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        instance = instance._model_instance
        return super().__get__(instance, cls)

