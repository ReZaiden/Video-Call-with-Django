from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from .models import VideoCall, User
from django.contrib.auth import authenticate, login

class VideoCallView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            call_logs = VideoCall.objects.filter(Q(caller=user) | Q(receiver=user)).order_by('-call_start_time')
            context = {'call_logs': call_logs}

            return render(request, 'VideoCall/videocall.html', context=context)
        else:
            return HttpResponseRedirect("/login/")


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('')
        return render(request, 'VideoCall/login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('')
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        type = request.POST.get('type', None)
        print(username, password, type)
        if username and password:
            if type == "signin":
                print("signin")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect("/login/")
            elif type == "signup":
                print("signup")
                email = request.POST.get('email', None)
                user = User.objects.create_user(username=username, password=password, email=email)
                login(request, user)
                return HttpResponseRedirect('/')

