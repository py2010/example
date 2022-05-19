# coding=utf-8

# from django.db.models.fields import reverse_related as _dj


# class ManyToOneRel(_dj.ManyToOneRel):
#     '''反向外键'''

#     def get_cache_name(self):
#         # 为了防止虚拟字段刚好和model本身字段重名, 虚拟关联字段加~
#         cache_name = super().get_cache_name()
#         return f'~{cache_name}'


# class OneToOneRel(ManyToOneRel):
#     1

