from django.db import models

from generic import vr
# Create your models here.


class User(models.Model):
    SEX = (
        (1, "男"),
        (2, "女"),
    )
    name = models.CharField("名称", max_length=20, default='abc', db_index=True)
    sex = models.SmallIntegerField("性别", choices=SEX, null=True, blank=True)

    p = models.SmallIntegerField("P", null=True, blank=True)
    one = models.SmallIntegerField("One", null=True, blank=True)

    class Meta:
        # ordering = ['name']
        verbose_name = '用户'

    def __str__(self):
        return self.name

    class VirtualRelation(vr.VR):
        one = vr.OneToOneField('a.One', verbose_name="One", db_column='one', related_name='user')
        p = vr.ForeignKey('a.P', verbose_name="P", db_column='p')


class Host(models.Model):

    ASSET_STATUS = (
        (1, "在用"),
        (2, "备用"),
        (3, "故障"),
        (4, "下线"),
        (6, "其它"),
    )

    ASSET_TYPE = (
        (1, "物理机"),
        (2, "虚拟机"),
        (3, "容器"),
        (4, "交换机"),
        (6, "其它")
    )

    name = models.CharField(max_length=20, verbose_name="名称", db_index=True)
    p = models.SmallIntegerField("机组", default=0, db_index=True)

    user = models.ForeignKey('User', verbose_name="用户", on_delete=models.SET_NULL, null=True, blank=True)

    status = models.SmallIntegerField("设备状态", choices=ASSET_STATUS, default=1, db_index=True)
    asset_type = models.SmallIntegerField("设备类型", choices=ASSET_TYPE, default=2, db_index=True)

    remark = models.CharField(max_length=50, verbose_name="说明", default='未填写', db_index=True)
    # create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    update_time = models.DateTimeField('最后修改', auto_now=True, blank=True, null=True)
    enable = models.BooleanField('启用', default=True)

    class Meta:

        # ordering = ['p', 'name']
        verbose_name = '主机'

    def __str__(self):
        return self.name

    class VirtualRelation(vr.VR):
        p = vr.ForeignKey('a.P', db_column='p', verbose_name="P", default=0)

