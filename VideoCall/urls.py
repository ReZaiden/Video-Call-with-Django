from django.urls import path

from VideoCall.views import VideoCallView, LoginView

urlpatterns = [
    path('', VideoCallView.as_view(), name='videocall'),
    path('login/', LoginView.as_view(), name='login'),
]