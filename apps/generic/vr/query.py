# coding=utf-8

from django.db.models import query as _dj
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor, ManyToManyDescriptor

'''
虚拟关联 -- 列表页数据预处理 -- SQL性能优化
使列表页在prefetch_related()原有功能上, 增加only()过滤查询字段

官方QuerySet有三个优化性能相关功能: select_related() prefetch_related() 和 only()
qs.select_related()关联表支持only()限定字段, 但左联不支持x2m关系, 且只能在同一数据库中查询
qs.prefetch_related()关联表可以跨库, 但不支持only()导致查出所有字段: select * from 关联表
'''


def prefetch_related_objects(model_instances, related_lookups):
    '''
    根据配制的虚拟关联关系, 将当前模型实例对象预绑定vr关联对象, 支持跨数据库表进行关联, 关联表查询增加only()
    '''
    if model_instances and related_lookups:

        for field_name, field_lookup in related_lookups.items():
            select_fields = field_lookup.get('select_fields', [])
            lookup_fields = field_lookup.get('lookup_fields', {})

            obj_list = prefetch_one_field(model_instances, field_name, select_fields)
            # if obj_list and lookup_fields:
            prefetch_related_objects(obj_list, lookup_fields)


def prefetch_one_field(model_instances, field_name, select_fields=[]):

    if field_name.startswith('~'):
        field_name = field_name[1:]
        model_instances = [instance._vr for instance in model_instances]

    if not select_fields:
        # x2o + o2x, 业务上SQL实际可以跳过中间关联表查询, 目前为简便程序CPU绑定实例, 会查中间表ID
        select_fields = ['pk']  # xxx(外键)__field(反向外键)__xxx
    elif '*' in select_fields:
        '''
        __末尾为关联字段时, 页面显示obj.__str__(), 无法一次性确定查询SQL, 这时有二种方案,
        一是SQL查询所有字段, 二是模板取数时大量单条where查询所需字段数据, 目前为第一种方案.
        如果有自定义模板, 需额外使用其它字段时, 可以自行指定prefetch_fields(list_fields)
        '''
        select_fields = []  # SQL查询所有字段, 如果不想表查所有字段, 字段配置时末尾应当为普通字段

    for obj in model_instances:
        if not hasattr(obj, '_prefetched_objects_cache'):
            try:
                obj._prefetched_objects_cache = {}  # model实例
            except (AttributeError, TypeError):
                return
    prefetcher, descriptor, attr_found, is_fetched = _dj.get_prefetcher(model_instances[0], field_name, field_name)

    if not prefetcher:
        raise AttributeError
    # prefetcher.select_fields = select_fields  # 传递参数到get_prefetch_queryset中qs.only(*fields)

    if isinstance(descriptor, (ReverseManyToOneDescriptor, ManyToManyDescriptor)):
        # x2m关联对应多条数据 (使用RelatedManager)
        queryset = super(prefetcher.__class__, prefetcher).get_queryset()
    else:
        queryset = prefetcher.get_queryset()
    queryset = queryset.only(*select_fields)

    lookup = _dj.Prefetch(field_name, queryset)
    obj_list, _ = _dj.prefetch_one_level(model_instances, prefetcher, lookup, level=0)
    return obj_list

