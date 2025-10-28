from django.contrib import admin
from .models import VideoCall

class VideoCallAdmin(admin.ModelAdmin):
    list_display = ('caller', 'receiver', 'call_start_time', 'call_end_time', 'status', 'duration')
    list_filter = ('status', 'call_start_time')
    search_fields = ('caller__username', 'receiver__username')

admin.site.register(VideoCall, VideoCallAdmin)
