# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.auth import get_user_model

from generic import vr

User = get_user_model()
Group = User.groups.rel.model


class B(models.Model):
    name = models.CharField("名称", max_length=30, default='bbb')

    class Meta:
        ordering = ['name']
        verbose_name = 'BB'

    def __str__(self):
        return self.name


class P(models.Model):
    name = models.CharField("名称", max_length=30, default='ppp')
    desc = models.CharField("描述", max_length=100, null=True, blank=True)
    b = models.ForeignKey(B, verbose_name="B", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = '外键表'

    def __str__(self):
        return self.name


class One(models.Model):
    name = models.CharField("名称", max_length=30, default='ooo')
    b = models.ForeignKey(B, verbose_name="B", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'o2o表'

    # def __str__(self):
    #     return self.name


class T(models.Model):
    name = models.CharField("名称", max_length=30, default='ttt')
    p = models.ForeignKey(
        P, verbose_name="P",
        related_name='t',
        on_delete=models.SET_NULL, null=True, blank=True)
    one = models.OneToOneField(
        One, verbose_name="One",
        related_name='t',
        on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'T'

    class VirtualRelation(vr.VR):
        # (vr.one.column == model.one.column)
        one = vr.OneToOneField(
            One, verbose_name="One",
            related_name='t',
            on_delete=models.SET_NULL, null=True, blank=True)

    # def __str__(self):
    #     return self.name

    # def __setattr__(self, k, v):
    #     if k == 'p_id':
    #         return
    #     print(k, v, '-----------')
    #     return super().__setattr__(k, v)

    # def __init__(self, *a, **k):
    #     super().__init__(*a, **k)
    #     # print(self.p, 888888)
    #     1


class M(models.Model):
    name = models.CharField("名称", max_length=30, default='mmm')
    # p = models.ForeignKey(
    #     P, verbose_name="P",
    #     related_name='m',
    #     related_query_name='m2',
    #     on_delete=models.SET_NULL, null=True, blank=True)
    # one = models.OneToOneField(
    #     One, verbose_name="One",
    #     db_column='one_id',
    #     # related_name='m',
    #     on_delete=models.SET_NULL, null=True, blank=True)
    p_id = models.SmallIntegerField("One++", null=True, blank=True)
    one_id = models.SmallIntegerField("One++", null=True, blank=True)

    t = models.ManyToManyField(
        T, verbose_name='T',
        # related_name='m',
        blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'M'

    class VirtualRelation(vr.VR):
        # 虚拟关系字段 db_column 需有对应model字段column (one.column == one_id)
        one = vr.OneToOneField(
            One, verbose_name="One",
            # db_column='one_id',
            related_name='m',
            on_delete=models.SET_NULL, null=True, blank=True)
        p = vr.ForeignKey(
            P, verbose_name="P",
            # db_column='p_id',
            related_name='m',
            related_query_name='m2',
            on_delete=models.SET_NULL, null=True, blank=True)

    # def __str__(self):
    #     return self.name


class M2T(models.Model):
    m = models.ForeignKey(M, verbose_name='M', on_delete=models.CASCADE)
    t = models.ForeignKey(T, verbose_name='T', on_delete=models.CASCADE)

    # m_id = models.SmallIntegerField('M')
    # t_id = models.SmallIntegerField('T')

    class Meta:
        verbose_name = 'M2T'
        # unique_together = [('m', 't'), ]

    class VirtualRelation(vr.VR):
        m = vr.ForeignKey(M, verbose_name='M', on_delete=models.CASCADE)
        t = vr.ForeignKey(T, verbose_name='T', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} - m: {self.m_id} t: {self.t_id} '
