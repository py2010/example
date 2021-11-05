from django.db import models

# from a.models import P, One, T
# Create your models here.


class Demo(models.Model):
    name = models.CharField("名称", max_length=30, default='demoooo')

    p_id = models.SmallIntegerField("P++", null=True, blank=True)
    one_id = models.SmallIntegerField("One++", null=True, blank=True)

    # p = models.ForeignKey(
    #     P, verbose_name="P",
    #     on_delete=models.SET_NULL, null=True, blank=True)
    # one = models.OneToOneField(
    #     One, verbose_name="One",
    #     on_delete=models.SET_NULL, null=True, blank=True)

    # t = models.ManyToManyField(
    #     T, verbose_name='T',
    #     blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Demo'

    # def __str__(self):
    #     return self.name


class Middle(models.Model):
    '''虚拟关联m2m中间表'''

    demo_id = models.SmallIntegerField('Demo')
    t_id = models.SmallIntegerField('T')

    class Meta:
        verbose_name = 'm2m中间表'
        unique_together = [('demo_id', 't_id'), ]

    def __str__(self):
        return f'跨库中间表 - Demo: {self.demo_id} <--> T: {self.t_id}'
