from django.urls import path

from VideoCall.views import VideoCallView

urlpatterns = [
    path('', VideoCallView.as_view()),
]