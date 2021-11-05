# -*- coding: utf-8 -*-


class MyRouter(object):
    # 配置数据库路由

    MAPPING = {
        # '应用名': {
        #     '模型名小写': '数据库',
        # },
        # 注意 allow_migrate传递过来的模型名为小写
        'vr': {
            # 虚拟关联示例
            # 'default_model': 'vr',
            'demo': 'vr',
            'middle': 'vr',
        },
    }

    def get_db(self, app_label, model_name, model=None):
        # print(app_label, model_name, kwargs, 55555555555)
        try:
            model_db = self.MAPPING[app_label][model_name.lower()]
        except Exception:
            model_db = 'default'
        return model_db

    def get_model_db(self, model):
        #  获取模型对应的db
        if model.__module__ == 'sicpay.models_gf':
            return 'gf'
        app_label = model._meta.app_label
        return self.get_db(app_label, model.__name__, model=model)

    def db_for_read(self, model, **hints):
        """
        建议用于读取“模型”类型对象的数据库。

        如果数据库操作可以提供有助于选择数据库的任何附加信息，
        它将在 hints 中提供。这里 below 提供了有效提示的详细信息。

        如果没有建议，则返回 None, 使用默认数据库。
        """
        # print(model, self.get_model_db(model), 333333333)
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
        db_obj1 = self.get_model_db(obj1.__class__)
        db_obj2 = self.get_model_db(obj2.__class__)
        if db_obj1:
            return db_obj1 == db_obj2

    # def allow_syncdb(self, db, model):
    #     # 兼容 Django 1.4 - 1.6
    #     app_label = model._meta.app_label
    #     model_name = model._meta.model_name
    #     return self.allow_migrate(db, app_label, model_name)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        '''
        Django 1.7 - 1.11 - 2.*
        控制是否允许 migrate, False为不允许, None表示没意见, 允许.
        框架传递过来的参数model_name 为小写的 _meta.model_name
        '''
        # print(db, app_label, model_name, hints, 88888888888)
        if db == 'java':
            # 不管 Meta.managed 是不是为 False, 都不migrate
            return False
        model = hints.get('model')
        if not model:
            # 未提供model参数
            return False
        if app_label in self.MAPPING:
            model_db = self.get_db(app_label, model_name, model=model)
            return model_db == db
