from django.db import models

from generic import vr
# from a.models import P, One, T
# Create your models here.


class Demo(models.Model):
    name = models.CharField("名称", max_length=30, default='demoooo')

    p_id = models.SmallIntegerField("P++", null=True, blank=True)
    one_id = models.SmallIntegerField("One++", null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Demo'

    # def __str__(self):
    #     return self.name

    class VirtualRelation(vr.VR):
        one = vr.OneToOneField(
            'a.One', verbose_name="One",
            db_column='one_id', related_name='demo',
            on_delete=models.SET_NULL, null=True, blank=True)
        p = vr.ForeignKey(
            'a.P', verbose_name="P",
            on_delete=models.SET_NULL, null=True, blank=True)


class Middle(models.Model):
    '''虚拟关联m2m中间表'''

    demo_id = models.SmallIntegerField('Demo')
    t_id = models.SmallIntegerField('T')

    class Meta:
        verbose_name = 'm2m中间表'
        unique_together = [('demo_id', 't_id'), ]

    def __str__(self):
        return f'跨库中间表 - Demo: {self.demo_id} <--> T: {self.t_id}'

    class VirtualRelation(vr.VR):
        '''
        虚拟字段必需和model普通字段的DB表字段名一致, 比如外键t默认为t_id,
        vr.t.column == 't_id' == model.t_id.column
        这里都是和django默认column一致, 所以无需指定 db_column='t_id'
        如果对应model中的t_id字段指定不同字段名, 比如db_column='t',
        则虚拟字段t也需指定 db_column='t'
        '''
        demo = vr.OneToOneField(
            Demo, verbose_name="Demo",
            related_name='middle',
            on_delete=models.SET_NULL, null=True, blank=True)
        t = vr.ForeignKey(
            'a.T', verbose_name="T",
            on_delete=models.SET_NULL, null=True, blank=True)

