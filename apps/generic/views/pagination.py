# coding=utf-8
import logging
from urllib.parse import quote
from math import ceil
from django.db.models import Q
from django.http import Http404
from django.core.paginator import Paginator
from django.conf import settings

logger = logging.getLogger()


class CursorPaginator(Paginator):
    '''
    在django页码分页基础上, 增加支持大数据游标分页, 解决大数据分页页面SQL打开慢的问题.
    市面上常见的游标分页基本是只能翻上一页下一页, 想往后翻非常累, 走向另一个极端--偏移为零,
    且只支持一个非重字段(unique=True)排序, 不支持多字段排序(也无意义, 首字段已是非重).
    而当前游标分页器可自定义配置偏移量, 且业务排序字段不限类型和数量, 按业务字段排序后,
    再按配置的cursor_unique_field非重字段排, 使结果为唯一序列, 可利用游标数据精确定位.

    原理: 当打开一个页面后, 将当前页首一条数据做为游标保存到前端, 之后打开其它页面时,
         不再是从第一页offset, 而是在前面打开页基础上, 相对小范围偏移获取新页数据.
         如果是非法翻页, 比如URL手工指定超出范围(向前或向后)的页码page=xxx,
         则将打开游标数据(向前或向后)最远能偏移的页面.

    注意: 如果排序字段有Null值, 请使用 NullFieldCursorPaginator 分页器
         游标缺点是当数据有修改变化时, 唯一序列不一定是实时的, 而是基于打开第一页时当时状态.
         游标后面的数据有修改时, 修改后仍然在游标后面, 则不会有影响.
         但游标前面的数据(排序字段数据)有变动, 可能会产生影响, 比如序号变化, 排序位置变化.

    self.OFFSET_MAX: 当查询符合条件的数据少于值, 则为常规页码分页, 否则切换为游标分页.
                     数值越大, 往后翻页最大步进就越大, 太大则SQL偏移性能就慢.
                     表数据很多, 但想快翻到后页, 结合数据库性能, 可适当把数值设大.
    self.cursor_unique_field: 必需为表中不含重复数据的字段, 比如主键或unique=True的字段,
                              如果配置的字段可能含相同数据, 导致排序时无法生成唯一序列,
                              游标定位时可能会产生偏差, 重复概率越大偏差越大.
    '''
    before = 0  # 前面有多少条数据, 因为大数据游标分页后, 当前分页器只包含一部分范围的数据
    count_end = False  # count_check() 数量探索到末尾

    def init(self, view):
        # 将View参数传递到分页器
        self.OFFSET_MAX = view.cursor_offset_max
        self.cursor_unique_field = view.cursor_unique_field
        if self.cursor_unique_field in ('pk', '-pk'):
            # self.cursor_unique_field = queryset.get_meta().pk.name
            pk = view.model._meta.pk.name
            self.cursor_unique_field = f'-{pk}' if self.cursor_unique_field.startswith('-') else pk

    def paginate_queryset(self, page_number, page_object_list):
        # 大数据游标分页
        try:
            page_obj = self._get_page(page_object_list, page_number, self)
            # self.encode_cursor(page_number, page_obj.object_list)
            return (self, page_obj, page_obj.object_list, page_obj.has_other_pages())
        except Exception:
            raise

    def get_page_number(self, page):
        page_max = ceil((self.cursor.sn + self.OFFSET_MAX) / self.per_page)
        page_min = ceil((self.cursor.sn - self.OFFSET_MAX) / self.per_page)
        if page == 'last':
            return page_max
        try:
            page_number = min(int(page), page_max)
        except ValueError:
            raise Http404(f'错误页码: {page}')
        return max(page_number, page_min, 1)

    def check_cursor(self, cursor, page):
        # 根据前端游标和页码参数, 进行初始化检查及游标定位取数, 生成最终合法页码及对应的页数据
        self.check_cursor_unique_field()
        self.cursor = Cursor(cursor, self.get_queryset_order_by(), self.OFFSET_MAX)

        page_number = self.get_page_number(page)
        if self.cursor.sn and page_number > (self.OFFSET_MAX / self.per_page) * 0.7:
            # 在最大偏移量以内的小页码, 可以按需不使用游标定位, 系数<=1, 建议>0.4,
            # 减少因数据变动导致唯一序列变化带来的影响, 不用翻到第一页才刷新唯一序列.
            page_number, offset, reverse = self.get_offset(page_number)  # 游标偏移
            return page_number, self.cursor_queryset(offset, reverse)  # 游标定位取数
            # if self.count_end and page_number > self.num_pages:
            #     raise Http404('本页结果为空, 非法翻页或者可能有数据已删除, 导致最大页码已减小.')
        else:
            # 无游标定位, 对整个唯一序列进行刷新(游标分页时)
            count_max = self.count_check(self.object_list, page_number * self.per_page + self.OFFSET_MAX)
            self.count_set(count_max, True)

            bottom = (page_number - 1) * self.per_page - self.before
            top = bottom + self.per_page
            if top + self.orphans >= self.count:
                top = self.count
            return page_number, self.object_list[bottom:top]

    def get_offset(self, page):
        # 通过游标当前位置和待打开页面, 生成游标偏移方向及大小
        reverse = False  # 向前翻页, 表示反向排序偏移游标
        sns = range((page - 1) * self.per_page + 1, page * self.per_page + 1)  # page页数据序号
        if self.cursor.sn in sns[1:-1]:
            # 通常为page_size改变, 刚好打开游标所在页内, 游标相邻二侧数据都在页内,
            # 此时需向前和向后取数, SQL需反序和顺序查询二次, 为简化处理, 后翻一页.
            page += 1
            sns = range((page - 1) * self.per_page + 1, page * self.per_page + 1)  # page页数据序号
        logger.debug(f'当前页面序号: {[i for i in sns]}')
        if self.cursor.sn >= sns[-1]:
            # 向前翻页
            reverse = True
            self.before = sns[0] - 1
            offset = sns[-1] - self.cursor.sn
        elif self.cursor.sn <= sns[0]:
            # 向后翻页
            self.before = self.cursor.sn - 1
            offset = sns[0] - self.cursor.sn
        return page, offset, reverse

    def cursor_queryset(self, offset, reverse=False):
        '''
        queryset 是唯一序列的所有数据集, 去掉游标位置之前/后的数据, 取游标之后/前的所有数据集,
        为了SQL性能, 定位使用where过滤而不是offset, 且生成新的queryset而不提交事务查询IO,
        因为新queryset后续还需要进行取分页数据(有小范围offset).

        特殊情况offset为0, 表示打开页包含游标数据本身, reverse=True 页尾为游标, False则页首为游标.
        '''

        qs = self.get_cursor_filter(offset, reverse)  # 使用游标过滤数据, 用于后续小范围偏移取数

        if reverse:
            # 向前翻页, 由于QuerySet不支持取末尾切片数据, 更不能为此提交数据库IO查询所有数据集,
            # 将qs反向排序, 再从游标偏移取得页数据切片, 返回逆序对象 (为了SQL性能, 仍然懒处理)
            self.count_set(min(self.cursor.sn_max - self.before, self.OFFSET_MAX + self.per_page))
            # return qs[offset - self.per_page: offset]
            qs = qs.order_by(*[
                i[1:] if i.startswith('-') else f'-{i}'
                for i in self.cursor.order_by
            ])
            return Reverse(qs[abs(offset): self.per_page + abs(offset)])  # 反序数据再逆序, 负负得正使顺序不变
        else:
            # 向后翻页
            count_max = offset + self.OFFSET_MAX + self.per_page
            if self.before + count_max > self.cursor.sn_max:
                # 向后翻页时需探索新的最大数量
                count = self.count_check(qs, count_max)
                # print(f'count_max: {count}')
                self.count_set(count, True)  # ############
                if count < count_max:
                    # 探索到末尾 (比如页后面数据量小于OFFSET_MAX)
                    self.count_end = self.cursor.sn_max
            else:
                # 数据量末超过之前探索的最大值, SQL无需count(*)探索数量
                # 比如翻页到远页, 再向前翻页很多, 然后又向后翻页, 但未超出之前最远页面
                self.count_set(count_max)  # ############
            return qs[offset: offset + self.per_page]

    def get_cursor_filter(self, offset, reverse=False):
        # 根据游标定位数据, 进行过滤, 正向则取游标后面数据, 反向则取游标前面数据
        # 因排序字段不一定唯一, 普通字段需排除与游标相等的数据, cursor_unique_field字段则包含与游标相等数据
        qs_Q_args = []  # Q过滤条件, 内AND外OR
        fields = {}
        for index, ofield in enumerate(self.cursor.order_by):
            lookup = 'gt' if get_bool(not ofield.startswith('-'), not reverse) else 'lt'
            field = ofield[1:] if ofield.startswith('-') else ofield
            val = self.cursor.vals[index]
            if val is None:
                raise Exception(
                    f'当前游标分页器{self.__class__}只支持非Null字段排序,\n'
                    '如果排序字段含Null数据, 请修改游标分页器配置, 比如使用 NullFieldCursorPaginator'
                )
            equal = 'e' if self.cursor_unique_field in (field, f'-{field}') else ''
            # equal, 查询集包含游标数据本身, 使特殊情况下, 游标刚好在页首尾的也可支持 (而范围sns[1:-1]内将后翻一页)

            kwargs = {f'{field}__{lookup}{equal}': val}
            qs_Q_args.append(Q(**fields, **kwargs))
            # if field == self.cursor_unique_field:
            #     break  # 因为字段无重复数据, 再按之后的排序字段进行排序无意义
            fields[field] = val

        q = Q(*qs_Q_args)
        q.connector = 'OR'  # 写法兼容django 1.x
        return self.object_list.filter(q)

    def check_cursor_unique_field(self):
        # 检查queryset排序, 必需为唯一序列, 业务排序字段最后面自动加上cursor_unique_field进行排序
        order_by = self.get_queryset_order_by()
        if self.cursor_unique_field not in order_by and f'-{self.cursor_unique_field}' not in order_by:
            # queryset 必需是唯一序列, 所以按业务排序后再按unique_field排, 当表数据不再变化时, 各数据排序位置固定.
            order_by += (self.cursor_unique_field,)
            self.object_list = self.object_list.order_by(*order_by)

    def get_queryset_order_by(self):
        q = self.object_list.query
        return q.extra_order_by or q.order_by or (q.default_ordering and q.get_meta().ordering) or ()

    def count_check(self, queryset, _max=None):
        # 向后翻页, 探索打开的页面之后还有多少数据量, 探索量最大不超过_max
        # 为了count(*)性能只探索小范围, 且删除排序, 因为探索游标位置后面还有多少数量和排序无关
        if not _max:
            _max = self.OFFSET_MAX + self.per_page
        qs = queryset[:_max]
        qs.query.clear_ordering(True)  # 排序字段未建索引时, 大表count()性能很差
        return qs.count()

    def count_set(self, count, save=False):
        '''游标分页时, 为了SQL性能, 设置self.count值, 使避免用户业务程序SQL count(*)统计所有数量'''
        self.count = count + self.before
        if save:
            # 探索得的最大数量, 保存到游标中, 使打开前面页面不用再探索数量 (向前翻页时)
            self.cursor.sn_max = self.count

    # def encode_cursor(self, page, object_list):
    #     # 因为分页queryset不提交IO, 不支持取queryset[-1], 所以统一取第一条obj=queryset[0]生成游标
    #     print('生成游标定位数据')
    #     if isinstance(object_list, Reverse):
    #         # 向前翻页, 页数据最后一条做为游标 (因为向前翻页时从游标反方向查, 查询结果排序相反)
    #         sn = (page) * self.per_page
    #         obj = object_list[-1]  # object_list.queryset[0]
    #     else:
    #         # 向后翻页, 页数据第一条做为游标
    #         sn = (page - 1) * self.per_page + 1
    #         obj = object_list[0]

    #     order_by = self.get_queryset_order_by()
    #     vals = [str(getattr(obj, field[1:] if field.startswith('-') else field)) for field in order_by]
    #     data = '%00'.join(vals)

    #     self.url_cursor = f"{sn}/{self.cursor.sn_max}:{','.join(order_by)}%00{data}"

    # def page(self, number):
    #     """Return a Page object for the given 1-based page number."""
    #     number = self.validate_number(number)
    #     bottom = (number - 1) * self.per_page - self.before
    #     top = bottom + self.per_page
    #     if top + self.orphans >= self.count:
    #         top = self.count
    #     return self._get_page(self.object_list[bottom:top], number, self)


class Reverse:
    '''
    逆序器, 使queryset反向时, 在数据使用前懒处理, 不会提交数据库IO,
    使页面数据不是一次性查出所有字段数据, 而是可以按需要只查询部分字段.
    '''

    def __init__(self, queryset):
        self.queryset = queryset

    def __len__(self):
        return self.queryset.__len__()

    def __iter__(self):
        for obj in reversed(self.queryset):
            yield obj

    def __getitem__(self, k):
        #  0  1  2  3 ....
        # -1 -2 -3 -4 ....
        if isinstance(k, int):
            i = abs(k) - 1 if k < 0 else - k - 1
            return self.queryset.__getitem__(i)
        raise  # 切片场景暂时用不上
        self.queryset._fetch_all()
        list(reversed(self.queryset._result_cache))[k]

    def __getattr__(self, attr):
        # print(attr, 111111)
        return getattr(self.queryset, attr)


class Cursor:
    '''游标数据'''
    sn = 0  # 序号, 当前游标位置
    sn_max = 0  # p.count_check() 数量探索得到的最大序号值, 用于减少count(*)探测, 比如向前翻页时无需再查

    def __init__(self, cursor, qs_order_by, offset_max):
        self.order_by = ()  # 游标排序
        self.vals = []  # 游标排序字段对应值
        self.offset_max = offset_max
        try:
            self.decode_cursor(cursor, qs_order_by)
        except Exception as e:
            logger.info(f'游标解析出错, 忽略游标.\n{e}')

    def __bool__(self):
        # 是否游标分页
        return bool(self.sn) or self.sn_max >= self.offset_max

    @staticmethod
    def encode_cursor(page_obj):
        '''
        生成游标URL参数供前端使用. 当前功能只用在HTML模板调用,
        因为分页object_list还未提交IO查出页面数据, 以免SQL查出所有字段
        '''
        object_list = list(page_obj.object_list)  # 为防止select *, 必需是在此之前已提交了IO查出结果
        if object_list:
            obj = object_list[0]  # 当前页面首条数据做为游标
            sn = (page_obj.number - 1) * page_obj.paginator.per_page + 1  # 游标序号
            order_by = page_obj.paginator.get_queryset_order_by()
            vals = [getattr(obj, field[1:] if field.startswith('-') else field) for field in order_by]
            data = '%00'.join(StrNone.to_uri(vals))
            # data = '%00'.join(vals)
            return f"{sn}/{page_obj.paginator.cursor.sn_max}:{','.join(order_by)}%00{data}"
        raise Http404('本页结果为空, 非法翻页或者可能有数据已删除, 导致最大页码已减小.')

    def decode_cursor(self, cursor, qs_order_by):
        '''
        URL参数示例: 9999/10000000000:name,id\x00名称\x00号码123
                 游标序号/历史探索到最大序号:{*排序字段}\x00{*各字段对应数据}
        '''
        if cursor:
            sn, cursor = cursor.split('/', 1)
            sn_max, cursor = cursor.split(':', 1)
            self.sn_max = max(int(sn_max), self.sn_max)  # #########
            ordering, cursor = cursor.split('\x00', 1)
            self.order_by = tuple(ordering.split(','))
            self.vals = StrNone.to_python(cursor.split('\x00'))
            if self.validate(qs_order_by):
                self.sn = int(sn)
            else:
                logger.warning(f'因页数据排序规则改变, 前端提供的游标已过期.\n')

    def validate(self, qs_order_by=()):
        # 为简化处理, 排序参数只支持字符串, 比如qs.order_by('xx__xxx', 'xx')
        # 不支持OrderBy对象, 比如用户自定义queryset.order_by(OrderBy(**))
        # 复杂情况请根据实际业务需求继承重写.
        if len(self.order_by) == len(self.vals):
            return self.order_by == tuple(qs_order_by)
        raise Exception('游标数据异常.')


def get_bool(*args):
    '''
    多参数判断正反方向, 二次假为真, 类似负负得正
    (为便于理解使用负负得正. 仅从实现功能角度, 也可设定真真为假, 则正反相反, 只处理True)
    1. 翻页方向: 正向---向后翻页,  反向---向前翻页
    2. 排序方向: 正向---字段正序,  反向---字段倒序(以'-'开头)
    3. 空值方向: 正向---NULL最大, 反向---NULL最小
    '''
    res = 1  # 1为正(True), -1为反(False)
    for arg in args:
        res *= 1 if arg else -1  # 只处理False (反向)
    return True if res == 1 else False


# ************************************  分隔线  ************************************ #

'''
大数据游标分页 -- 游标定位支持Null数据排序
只详细测试mysql(null最小)和pg(null最大)定位一丝不差非常精确, sqlite/oracle简单试了下也正常.

考虑到Null值功能开发的时间碎片化间隙化, 可能会有一些兼容考虑不周, 暂时不作为MyListView默认分页器,
目前null只是先堆积代码实现功能再说, 简单处理一下做为示范, 以后有机会多使用再进行调整优化,
只有实际场景使用时, 开发和排错才比较直观.

为了数据库性能和索引效率, 建议排序字段都应当为非Null索引字段, 只对接第三方非标数据库才做Null处理.

注意:
django字段排序支持指定null最小/最大, 当前为简化处理只按不同数据库类型默认顺序来处理: check_null_order()
所以QuerySet.order_by()有指定null排最前或最后时会有问题, 大家按需扩展开发, 比如排序比较时需额外处理.
'''


class StrNone:
    '''
    游标定位数据, 排序字段值为Null时, 需做转换处理, 字符串转None.
    为防止和数据库字段本身正常数据混淆, 目前使用"\x10"表示None,
    如果有排序字段数据本身刚好为"\x10"的情况, 请修改cls.string
    '''
    string = '%10'  # 网址游标参数, 使用"\x10"表示None值 ("\x10" URL转义为 "%10")

    @classmethod
    def null(cls, val):
        # 检查排序字段值是否为None
        return quote(val) == cls.string

    @classmethod
    def to_python(cls, vals):
        # 将网页参数游标中表示空值的\x10还原为原值None
        return [None if cls.null(val) else str(val) for val in vals]

    @classmethod
    def to_uri(cls, vals):
        # 将游标排序字段None转URL参数
        return [StrNone.string if val is None else str(val) for val in vals]


class NullFieldCursorPaginator(CursorPaginator):
    '''
    可支持排序字段为Null的数据进行游标分页
    原理: 比如mysql (nulls_first=True), Null最小, 游标定位取小于游标排序字段的数据时,
          where 语句增加null条件 (field <= xxx or field is null),
          mysql取大于游标的数据条件不变.
          其它二个数据库nulls_last=True, 取游标前面数据时where条件不变, 取后面数据时,
          增加null条件 field >= xxx or field is null
    '''

    def get_cursor_filter(self, offset, reverse=False):
        # 根据游标定位数据, 进行过滤, 正向则取游标后面数据, 反向则取游标前面数据
        # 因排序字段不一定唯一, 普通字段需排除与游标相等的数据, cursor_unique_field字段则包含与游标相等数据
        NULLS_FIRST = check_null_order(self.object_list)  # True表示Null值最小, False表示Null最大
        qs_Q_args = []  # Q过滤条件, 内AND外OR
        fields = {}
        for index, ofield in enumerate(self.cursor.order_by):
            lookup = 'gt' if get_bool(not ofield.startswith('-'), not reverse) else 'lt'
            field = ofield[1:] if ofield.startswith('-') else ofield
            _bool = get_bool(not NULLS_FIRST, not reverse, not ofield.startswith('-'))

            val = self.cursor.vals[index]
            equal = 'e' if field == self.cursor_unique_field or f'-{field}' == self.cursor_unique_field else ''
            # equal, 查询集包含游标数据本身, 使特殊情况下, 游标刚好在页首尾的也可支持 (不支持范围 sns[1:-1])

            if val is None:
                # if get_bool(_bool, equal):
                if equal:
                    if _bool:
                        # 比如 field <= None (Null最小) or field >= None (Null最大)
                        kwargs = {f'{field}__isnull': True}
                    else:
                        kwargs = {}  # 所有数据都符合
                else:
                    if _bool:
                        # 比如 field < None (Null最小) or field > None (Null最大)
                        # continue
                        kwargs = None  # 所有数据都不符合, 只加入字段到fields
                    else:
                        kwargs = {f'{field}__isnull': False}

            else:
                kwargs = {f'{field}__{lookup}{equal}': val}
                if _bool:
                    if is_null_field(self.object_list.model, field):
                        # model字段 null=True 允许为空
                        kwargs[f'{field}__isnull'] = True  # where增加OR条件: 包含排序字段值为None的数据
            if kwargs is not None:
                q = Q(**kwargs)
                q.connector = 'OR'  # django 1.x
                qs_Q_args.append(Q(**fields) & q)
            if val is None:
                fields[f'{field}__isnull'] = True  # 排序字段值为None
            else:
                fields[field] = val

        q = Q(*qs_Q_args)
        q.connector = 'OR'  # 写法兼容django 1.x
        return self.object_list.filter(q)


def is_null_field(model, field_name):
    field = model._meta.get_field(field_name)
    return field.null


def check_null_order(queryset):
    # 数据库字段数据排序, Null最小还是最大
    NULLS_FIRST = {
        'mssql': True,
        'mysql': True,
        'sqlite': True,
        # 'sqlite': False,
        'postgre': False,
        'oracle': False,
    }
    db = queryset.db
    engine = settings.DATABASES[db]['ENGINE']
    for k, v in NULLS_FIRST.items():
        if k in engine:
            return v
    raise Exception('未知数据库类型, 请手工增加指定')
