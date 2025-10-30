from django.urls import path
from .consumers import VideoCallConsumer

websocket_urlpatterns = [
    path('ws/video_call/', VideoCallConsumer.as_asgi(), name='video_call'),
]