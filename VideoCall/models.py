from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class VideoCall(models.Model):
    caller = models.ForeignKey(User, related_name='calls_made', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='calls_received', on_delete=models.CASCADE)
    call_start_time = models.DateTimeField(auto_now_add=True)
    call_end_time = models.DateTimeField(null=True, blank=True)
    status_list = [
        ('RINGING', 'Ringing'),
        ('CONNECTED', 'Connected'),
        ('ENDED', 'Ended'),
        ('MISSED', 'Missed'),
    ]
    status = models.CharField(max_length=10, choices=status_list, default='RINGING')

    def end_call(self, status):
        self.call_end_time = models.DateTimeField(auto_now=True)
        self.status = status
        self.save()

    @property
    def duration(self):
        if self.call_end_time:
            return self.call_end_time - self.call_start_time
        return timezone.now() - self.call_start_time

    def __str__(self):
        return f"Call from {self.caller.username} to {self.receiver.username} at {self.call_start_time}"
