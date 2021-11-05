# -*- coding: utf-8 -*-

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from allapp import URLS_APPS

ws_urlpatterns = []
for app_urls in URLS_APPS.values():
    # 从各app中收集ws_url
    try:
        ws_urlpatterns.extend(app_urls.ws_urlpatterns)
    except Exception:
        # print(e)
        pass


# import ipdb;ipdb.set_trace()
application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter(ws_urlpatterns)
    ),

})

