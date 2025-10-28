from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .models import VideoCall

class VideoCallView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            call_logs = VideoCall.objects.filter(Q(caller=user) | Q(receiver=user)).order_by('-call_start_time')
            context = {'call_logs': call_logs}

            return render(request, 'VideoCall/videocall.html', context=context)
        else:
            return HttpResponse("Unauthorized", status=401)
