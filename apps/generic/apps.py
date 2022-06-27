# coding=utf-8

from django.apps import AppConfig


class GenericConfig(AppConfig):
    name = 'generic'
    verbose_name = '通用视图模板(LowCode)'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     '''
    #     1. 使虚拟关联配置支持 app.model.VirtualRelation 的方式进行关联.
    #         (在model中统一且易于理解, 在view中尤其配置多层关联, 极不直观, 且不同view重复配置)
    #     2. 为支持在反向model中使用虚拟关联, 需在正向model中给关联model增加虚拟字段.
    #         field.contribute_to_class() ==> field.contribute_to_related_class()
    #     3. 为给反向model增加属性, 在各app.Model生成前, 重写django Model功能.
    #         (也可免猴子补丁在self.ready中处理, 但需for检索models增加处理量)
    #     4. 根据 django.apps.populate() 流程, 在所有app_config.import_models()前打补丁.
    #     '''
    #     from django.db import models
    #     # 所有app模型初始化之前, 猴子补丁
    #     models.Model.add_to_class

    # def import_models(self):
    #     # 当前app模型注册/初始化
    #     models = super().import_models()
    #     return models

    # def ready(self):
    #     # 所有app模型注册/初始化完成
    #     from django.apps import apps
    #     for model in apps.get_models():
    #         if hasattr(model, 'VirtualRelation'):
    #             print(model.VirtualRelation, 666666)

