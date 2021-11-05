# -*- coding: utf-8 -*-

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xyf.settings")
django.setup()
application = get_default_application()


# class MyApplication:
#     ...
