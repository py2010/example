# coding=utf-8

# import traceback
# import time
# import json
import random
import logging
from django.db.models import Max

from django.core.management.base import BaseCommand
from ... import models

logger = logging.getLogger()


class Command(BaseCommand):

    help = '''
    批量添加随机测试数据, 用于大数据游标测试.
    比如添加十万条数据: manage.py data 100000
    '''

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='?', default='a', type=str,
                            help=u'''指定model表, 比如'u'表示User, 'h'表示Host, 'a'表示所有.''')
        parser.add_argument('n', nargs='?', default=100, type=int,
                            help=u'''添加新数据条数''')

    def handle(self, *args, **options):
        logging.getLogger('django.db.backends').setLevel(logging.INFO)  # SQL DEBUG日志太多, 不显示

        model = options['model']
        n = options['n']
        print(f"********* 添加数据条数: {n} *********")
        if model in ('u', 'a'):
            add_datas(models.User, n)

        if model in ('h', 'a'):
            max_user_id = models.User.objects.aggregate(mid=Max('id'))['mid']
            if max_user_id:
                max_user_id = int(max_user_id)
            add_datas(models.Host, n, max_user_id)


def add_datas(model, n=200000, *args, **kwargs):
    max_id = int(model.objects.aggregate(mid=Max('id'))['mid'] or 0)

    print(f"\n{model}添加随机数据.....")
    objs = []
    sn, max_id = max_id, max_id + n
    func = globals().get(f'new_{model.__name__.lower()}') or new
    while sn < max_id:
        sn += 1
        data = func(sn, *args, **kwargs)
        obj = model(**data)
        objs.append(obj)
        if len(objs) >= 50000:
            model.objects.bulk_create(objs)
            print(f'已添加 {len(objs)} 条数据.')
            objs.clear()
    model.objects.bulk_create(objs)
    print(f"{model}添加完成.\n")


def new_user(sn):
    ns = (
        '李王张刘陈杨黄赵周吴徐孙朱马胡郭林何高梁郑罗宋谢唐韩曹许邓萧冯曾'
        '程蔡彭潘袁于董余苏叶吕魏蒋田杜丁沈姜范江傅钟卢汪戴崔任陆廖姚方金'
        '邱夏谭韦贾邹石熊孟秦阎薛侯雷白龙段郝孔邵史毛常万顾赖武康贺严尹钱'
        '施牛洪龚汤陶黎温莫易樊乔文安殷颜庄章鲁倪庞邢俞翟蓝聂齐向申葛岳'
    )
    ns1 = (
        '琼桂娣璐娅琦晶妍茜秋珊莎黛青倩婷姣婉娴瑾颖露瑶怡婵雁蓓仪荷丹蓉眉君'
        '琴蕊薇菁梦岚苑婕馨瑗琰韵园艺咏卿聪澜悦昭冰爽琬茗羽希欣飘育滢馥筠柔'
        '竹霭凝晓欢霄枫芸菲寒伊宜舒影荔枝思丽秀娟英慧巧美娜静淑惠珠翠雅芝玉'
        '萍红娥玲芬芳燕彩春菊珍贞莉兰凤洁梅琳素莲真环雪爱妹霞香月莺媛艳瑞佳'
    )
    ns2 = (
        '全利茂强山翔兴信清斌诚贵国时冠震善彪鹏固刚亮世广彬树建士星德发学言'
        '琛旭功翰朗胜裕宏成杰权晨豪波岩军东策承峰祥磊友超雄轮致达富钧生飞榕'
        '保坚涛伯绍炎新泰光鸣天才永平良乐哲维腾进俊航敬泽启毅壮行义弘明福博'
        '盛华浩风云政伟厚辉志海谦勇顺邦朋民嘉庆勤振仁楠群力昌健中松辰栋伦奇'
    )
    sex = get_random('12')
    if sex == '1':
        names = ns2
    elif sex == '2':
        names = ns1
    else:
        names = f'{ns1}{ns2}'

    data = {
        'pk': sn,
        'name': f'{random.choice(ns)}{random.choice(names)}',
        'sex': int(sex) if sex else None,
        'p': int(get_random('1234') or 0) or None,
    }
    return data


def new_host(sn, max_user_id=None):
    # return
    user_id = None
    if max_user_id:
        user_id = f'{random.randint(1, max_user_id)}'
        if not models.User.objects.filter(id=user_id).exists():
            user_id = None

    data = {
        'pk': sn,
        'name': f'n{random.randint(0, 99999)}',
        # 'p': get_random('1234', 0),
        'p': int(get_random('1234', 0)),
        'user_id': user_id,

        'status': int(get_random('12346', 0)),
        'asset_type': int(get_random('12346', 0)),
        'remark': ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 8)),
    }
    # print(data.get('user_id'), 9999999)
    return data


def new(sn):
    return {'pk': sn, 'name': f'n{random.randint(0, 99999)}'}


def get_random(iterobj, null=0.2):
    # null * 100 (None百分概率)
    if random.randrange(100) < null * 100:
        return None
    return random.choice(iterobj)

