from django.urls import path
from .consumers import ChatConsumer,NotificationConsumer,VideoCallConsumer

 
websocket_urlpatterns=[
    path('ws/chat/<str:room_name>',ChatConsumer.as_asgi()),
    path('ws/video-call/<str:room_name>',VideoCallConsumer.as_asgi()),
    path('ws/notification/<str:username>',NotificationConsumer.as_asgi()),
]
