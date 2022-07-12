# coding=utf-8
import logging

from django.db import models
from django.views.generic import ListView as _ListView
# from django.db.models.constants import LOOKUP_SEP

from django.db.models.fields.reverse_related import ForeignObjectRel, ManyToOneRel
from django.db.models.fields.related import RelatedField, ForeignKey

from .base import TemplateMixin, MyMixin
from .. import conf
from .. import vr

logger = logging.getLogger()


class ListView(TemplateMixin, _ListView):
    '''
    列表页视图
    list_fields, 格式示例:
        [
            'pk',
            字段2,
            (外键字段4__字段2, 外键表字段2标识名),
            (外键字段4__外键字段3__字段3, 多层关联表字段3标识名称),
            (<多对多|反向外键>字段5__外键字段2, 字段2标识名),
        ]
    标识名可以省略, 将自动从Model取 field.verbose_name,
    支持多层__关联, 层数不限, 设置错误的字段项将忽略.
    '''
    # template_name = 'generic/_list.html'
    list_fields = []  # 列表页显示的字段

    def get_context_data(self, *args, **kwargs):
        # 根据用户权限，对应显示增删改查的链接/按钮
        action_perm = {
            # action: 对应的action权限码
            'create': 'add',
            'delete': 'delete',
            'update': 'change',
            'detail': 'view',
            # 'list': 'view',
        }
        model_perms = {
            # action: 操作权限
            action: self.request.user.has_perm(
                f'{self.model._meta.app_label}.{perm}_{self.model._meta.model_name}'
            )
            for action, perm in action_perm.items()
        }

        # 转视图名，用于模板 {% url view_name %}
        list_view_name = self.request.resolver_match.view_name  # app_name可能和meta.app_label不同
        view_name = list_view_name[:-5]
        for action, perm in model_perms.items():
            if perm:
                model_perms[action] = f'{view_name}_{action}'

        return super().get_context_data(model_perms=model_perms, *args, **kwargs)

    def get_queryset(self):
        self.list_fields = self.init_fields(self.list_fields) or [
            ('', self.model._meta.verbose_name, '', None)
        ]  # 列表页字段为空时, 只一列显示obj列表, 提供标识名.
        return super().get_queryset()

    def get_field(self, field_name, model):
        '''
        根据字段名, 获取对应的字段
        django正向外键/m2m字段未设置related_name时, 反向字段(x2m)名称会加上"_set"后缀
        '''
        try:
            return model._meta.get_field(field_name)
        except Exception:
            if field_name.endswith('_set'):
                if field_name[:-4] in model._meta.fields_map:
                    field = model._meta.fields_map[field_name[:-4]]
                    if field.get_accessor_name() == field_name:
                        # 正向字段未设置related_name时的反查字段, 名称匹配
                        return field
                    else:
                        '反查字段有设置 related_name, 无需加后缀"_set"或其它巧合的情况, 字段返回None'

            # logger.debug(f'字段获取失败: {e}')
            # # raise

    def init_fields(self, fields):
        # 处理 list_fields, 转field对象用以模板页显示标识名verbose_name, 去除错误配置的字段
        _fields = []
        for _field in fields:
            if isinstance(_field, str):
                field_path, verbose_name = _field, None
            else:
                field_path, verbose_name = _field[:2]

            field_info = self.get_field_info(field_path, verbose_name)
            if field_info:
                _fields.append(field_info)

        return _fields

    def get_field_info(self, field_path, verbose_name=None):
        # 通过多级__路径字段, 取末尾字段信息
        field_names = field_path.split('__')
        _field_names = []
        model = self.model
        fields = []
        for index, field_name in enumerate(field_names):
            if field_name == 'pk':
                field_name = model._meta.pk.name

            field = self.get_field(field_name, model)
            if not field:
                return

            _field_names.append(field_name)
            fields.append(field)
            if index + 1 < len(field_names):
                model = field.related_model

        if not verbose_name:
            if hasattr(field, 'verbose_name'):
                verbose_name = field.verbose_name
            else:
                # 反向关系字段 ForeignObjectRel, 使用对方model标识名称
                verbose_name = field.related_model._meta.verbose_name
        _field_path = '__'.join(_field_names)
        return _field_path, verbose_name, field_name, fields


class QueryListView(ListView):
    '''
    搜索过滤, filter_fields 配置格式同 list_fields
    '''
    filter_fields = []  # 使用模糊搜索多字段功能
    filter_orm_fields = conf.LISTVIEW_FILTER_ORM_FIELDS  # ORM过滤字段列表
    filter_orm_prefix = conf.LISTVIEW_FILTER_ORM_PREFIX  # 字段参数前缀

    def get_queryset(self):
        qs = super().get_queryset()
        if self.filter_orm_fields:
            qs = self.get_queryset_orm(qs, True)
        return self.get_queryset_search(qs)

    def get_queryset_search(self, queryset=None):
        '''
        模糊查询多字段, 各字段逻辑或
        外键使用<field>__关联表<field>,
        django不支持 <field>_id 模糊查询, 请使用 <field>__id 代替
        有自定义 field.get_prep_value()，lookup只能用exact，不支持icontains
        '''
        field_infos = self.init_fields(self.filter_fields)
        self.filter_fields = [f[0] for f in field_infos]
        self.filter_labels = [f[1] for f in field_infos]  # 搜索框提示名称

        if queryset is None:
            queryset = super().get_queryset()
        s = self.request.GET.get('s')
        if s and self.filter_fields:
            Q_kwargs = {f'{field}__icontains': s.strip() for field in self.filter_fields}
            # print(Q_kwargs, 77777777)
            q = models.Q(**Q_kwargs)
            q.connector = 'OR'  # 写法兼容django 1.x
            queryset = queryset.filter(q).distinct()
        return queryset

    def get_queryset_orm(self, queryset=None, ignore_error=False):
        '''
        使ListView支持GET参数ORM查询过滤，
        参数ignore_error, 当ORM字段参数错误时, 是否忽略, 不忽略则查询为空.
        本函数不考虑ORM外键过滤/攻击限制之类的需求，如有请根据model实例自定义。

        如果有其它类型的搜索过滤，则为逻辑与叠加操作过滤。

        示例：
        class xxxListView(xxx):
            xxxx
            get_queryset = get_queryset_orm
            或
            def get_queryset(self):return get_queryset_orm(self, True)

        http://xxx列表页/?city__name=深圳&field__icontains=xx
        相当于queryset.filter(city__name='深圳', field__icontains='xx')
        多个参数一律视为"和"，不支持“或”操作，因为URL的&只是间隔符，不含逻辑与或信息
        '''
        if queryset is None:
            queryset = super().get_queryset()
        for k, v in self.request.GET.items():
            if v and k.startswith(self.filter_orm_prefix) and (
                self.filter_orm_fields == '__all__' or k in self.filter_orm_fields
            ):
                # print('ORM_参数', k, v)
                try:
                    queryset = queryset.filter(**{k[len(self.filter_orm_prefix):]: v}).distinct()
                except Exception:
                    if ignore_error:
                        # 忽略错误的orm表达式参数
                        continue
                    return queryset.none()

        return queryset


class PageListView(QueryListView):
    '''
    分页ListView, 支持url请求参数:
        page: 页码
        pagesize: 每页条数 (最大限制100条)
    '''

    paginate_by = conf.LISTVIEW_PAGE_SIZE  # 每页条数
    # paginate_orphans = 3  # 尾页少于数量则合并到前一页

    page_kwarg = conf.LISTVIEW_PAGE_KWARG  # url页码参数名称
    page_size_kwarg = conf.LISTVIEW_PAGE_SIZE_KWARG  # url参数PageSize名称, 类似page_kwarg
    page_size_list = conf.LISTVIEW_PAGE_SIZE_LIST  # 前端PageSize选择列表
    js_table_data = None  # 开启DataTable.js前端表格分页

    def get_context_data(self, *args, **kwargs):

        pagesize = self.request.GET.get(self.page_size_kwarg)  # 每页显示条数
        try:
            self.paginate_by = min(100, int(pagesize))  # 限制最大100条
        except Exception:
            pass

        context_data = super().get_context_data(*args, **kwargs)
        if context_data.get('is_paginated'):
            # 生成url参数，用于各分页链接，不包含page=xx参数本身
            context_data['u_args'] = [
                f'{arg}={val}' for arg, val in self.request.GET.items() if arg != self.page_kwarg
            ]
            context_data['page_range'] = self.get_page_range(context_data['page_obj'])

        elif self.js_table_data is None:
            # 前端js分页，用户未指定True/False，且后端分页/搜索都未开启时, 开启前端js分页/搜索过滤
            self.js_table_data = not self.filter_fields and not self.filter_orm_fields
        return context_data

    def get_page_range(self, page_obj):
        # 大表分页时，优化页码显示
        page_range = page_obj.paginator.page_range
        num_pages = page_obj.paginator.num_pages
        if num_pages > 10:
            # 页数太多时不全显示，只显示当前页附近页码
            PAGES = 3  # 附近页数
            page_range_1 = max(1, page_obj.number - PAGES)  # 显示的起始页码
            page_range_2 = min(num_pages + 1, page_obj.number + 1 + PAGES)  # 显示的结束页码
            page_range = range(page_range_1, page_range_2)
        return page_range


class VirtualRelationListView(PageListView):
    '''
    表model实例, 全自动虚拟关联另一model实例, 无需自定义view和template.
    场景: 表关系业务上为"外键"关系, 但数据库结构上不是外键, 只是普通字段, 也无约束.
    原理: 两表关联时, SQL只查出二个表数据, 然后消耗CPU面向对象开发进行"连接", 后续不再有二表数据库IO操作.

    比如跨库虚拟关联, self.model 与 related_model 通过数据库普通字段建立虚拟外键关联,
    跨数据库的两表, SQL无法左联, 为提高SQL查询效率, 实现类似 prefetch_related 的功能.

    需在正向model中配置VirtualRelation虚拟关联关系后, 才可自动进行虚拟关联.
    两个Model如果有实际的关联关系, 也可同样配置model.VirtualRelation, 当成虚拟关联来处理,
    ListView.list_fields配置时, 为便于区分和防止重名, 虚拟关联字段以"~"开头.
    支持__多层关联, 层数不限, SQL单表查询每个model表, 且正常情况下只会查所需字段数据.
    末尾建议以普通字段结尾, 否则以关联字段结尾时, 最后字段模型SQL会查表所有字段 select * from
    '''

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        object_list类型通常为queryset, 默认来自self.object_list,
        列表页有分页时后续会进一步分页过滤, 然后再进行虚拟关联绑定关联表模型实例,
        关联绑定之后不可再进行qs.filter()过滤等操作, 以免生成新的queryset,
        导致模型实例重新生成, 绑定关系丢失, 且会导致页码数据变化, 业务上也无意义,
        任何过滤等操作应当在分页前进行, 另外注意qs.only()也会生成新的qs,
        ----> context[context_object_name] = queryset <----
        分页后的queryset本身引用不应再改变, 否则导致要重新context[xxx] = new_queryset
        '''
        if object_list is not None:
            kwargs['object_list'] = object_list  # 兼容django 1.* (object_list放在kwargs)
        context = super().get_context_data(**kwargs)
        self.prefetch_related(context['object_list'])  # 分页queryset模型实例绑定关联
        return context

    def prefetch_related(self, object_list):
        '''
        object_list 通常为分页后的 queryset, 从业务角度看, 分页数据后续不应再有qs.filter()等操作.
        当前函数不能在分页处理前执行, 以免分页过滤失效, 或者导致所有页数据都将进行关联绑定, 浪费处理.
        '''
        select_fields, lookup_fields = self.prefetch_fields()
        # print(select_fields, lookup_fields, 7777777788888888)
        if getattr(object_list, '_result_cache', []) is None:
            # 增加SQL查询字段, (queryset未提交IO)
            self.add_only_fields(object_list, select_fields)
        vr.prefetch_related_objects([obj for obj in object_list], lookup_fields)  # 分页SQL提交IO, 设置虚拟关联

    def prefetch_fields(self, list_fields=[]):
        # related = defaultdict(list)
        # related = {
        #     'select_fields': [],  # 普通字段, 用于SQL查询时限定字段
        #     'lookup_fields': {},  # 外键字段, 包括业务为外键关系的普通字段(虚拟外键)
        # }

        def add_field(field_name, field, super_lookup, is_last):
            select_fields = super_lookup.setdefault('select_fields', ['pk'])

            if isinstance(field, (RelatedField, ForeignObjectRel)):

                if isinstance(field, ForeignKey) and field_name == field.attname:
                    # ForeignKey.attname(), 只需将外键ID加入SQL查询字段列表, 无需查关联表
                    select_fields.append(field_name)
                    return

                lookup_fields = super_lookup.setdefault('lookup_fields', {})
                field_lookup = lookup_fields.setdefault(field_name, {})
                if is_last:
                    # 关联字段在最末尾, 没进一步指定显示字段, 页面显示字段所在模型 model.__str__()
                    field_lookup.setdefault('select_fields', []).append('*')
                if isinstance(field, ForeignKey):
                    # 正向外键, 一对一
                    if isinstance(field, vr.ForeignKey):
                        field = field.column_field  # 虚拟关联字段, select_fields对应model真实字段

                    if field.name not in select_fields:
                        # 外键字段, 加入上一级 SQL select 列表
                        select_fields.append(field.name)
                elif isinstance(field, ManyToOneRel):
                    # o2x 反向外键, 一对一
                    field_lookup.setdefault('select_fields', []).append(field.remote_field.column)
                return field_lookup
            else:
                # 普通字段(包含外键.attname()), 加入 SQL select 列表
                select_fields.append(field_name)

        lookup = {}
        for field_info in list_fields or self.list_fields:
            field_lookup = lookup
            field_path, verbose_name, last_field_name, fields = field_info
            if field_path:
                field_names = field_path.split('__')
                for index, field_name in enumerate(field_names):
                    field_lookup = add_field(field_name, fields[index], field_lookup, index + 1 == len(field_names))
                    if field_lookup is None:
                        # 末尾普通字段, 或配置错误的列表字段
                        break

        return lookup.get('select_fields'), lookup.get('lookup_fields')

    def get_field(self, field_name, model):
        if field_name.startswith('~'):
            return model.VirtualRelation.get_field(field_name[1:])
        else:
            return super().get_field(field_name, model)

    def add_only_fields(self, queryset, field_names=[]):
        '''
        SQL查询限定字段, 执行queryset.only(*field_names),
        如果多次执行only(), 按django设计的方案只有最后一次的only()有效,
        所以这里改成only追加字段的方式, 相当于在前一次only()限定字段基础上, 追加新字段.
        使用户ListView.queryset若有自定义的only(), 字段不会被删.
        '''
        if field_names:
            existing, defer = queryset.query.deferred_loading
            field_names = set(field_names)
            if 'pk' in field_names:
                field_names.remove('pk')
                field_names.add(self.model._meta.pk.name)

            if defer:
                # 用户queryset没进行only()自定义限定字段, defer()差集
                # return queryset.only(*field_names)
                field_names = field_names.difference(existing)
            else:
                # 在前一次限定字段基础上, 追加新限定字段, only()并集
                logger.debug(f'保留用户queryset已有的only限定字段: {existing}')
                field_names = existing.union(field_names)
            queryset.query.deferred_loading = field_names, False


class MyListView(MyMixin, VirtualRelationListView):
    '''
    # 使用示例:
    class XxxList(MyListView):
        model = models.Xxx
        list_fields = ['pk', 'm2o__o2o__pk', 'm2o__~o2m__name', ('~o2m__~m2o__name', '虚拟m2m = o2m + m2o')]
        filter_fields = ['field1', 'x2o__field3']
        filter_orm_fields = ['x2o__field3__icontains', 'create_time__date__lte']

    '''

