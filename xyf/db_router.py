# -*- coding: utf-8 -*-


class MyRouter(object):
    # 配置数据库路由

    MAPPING = {
        # '应用名': {
        #     'model_default_db': '应用名下模型默认的数据库',
        #     '模型名': '数据库',
        # },
        'vr': {
            # 虚拟关联示例
            'model_default_db': 'vr',
            # 'Demo': 'vr',
            # 'Middle': 'vr',
        },
        'b': {
            # 大数据游标分页
            'model_default_db': 'big',
        },
    }

    def get_model_db(self, model):
        #  获取模型对应的db
        if model.__module__ == 'pay.models.gf':
            return 'gf'
        app_label = model._meta.app_label
        if app_label in self.MAPPING:
            label_db = self.MAPPING[app_label]
            return label_db.get(model.__name__) or label_db.get('model_default_db')

    def db_for_read(self, model, **hints):
        """
        建议用于读取“模型”类型对象的数据库。

        如果数据库操作可以提供有助于选择数据库的任何附加信息，
        它将在 hints 中提供。这里 below 提供了有效提示的详细信息。

        如果没有建议，则返回 None, 使用默认数据库。
        """
        return self.get_model_db(model)

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        """
        如果允许 obj1 和 obj2 之间的关系，返回 True 。
        如果阻止关系，返回 False ，或如果路由没意见，则返回 None。
        这纯粹是一种验证操作，由外键和多对多操作决定是否应该允许关系。

        如果没有路由有意见（比如所有路由返回 None），则只允许同一个数据库内的关系。
        """
        # return True  # 允许跨库关联 (比如虚拟外键: Model为外键, DB为普通字段)
        db1 = self.get_model_db(obj1.__class__)
        db2 = self.get_model_db(obj2.__class__)
        if db1:
            return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        '''
        控制是否允许 migrate, False为不允许, None表示没意见(允许).
        框架传递过来的参数model_name 为小写的 _meta.model_name
        '''
        if db == 'java':
            # 不管 Meta.managed 是不是为 False, 都不migrate
            return False
        model = hints.get('model')
        if model:
            model_db = self.get_model_db(model)
            if model_db:
                return db == model_db
            elif db == 'default':
                return  # 未定义时, 使用default库
        return False

