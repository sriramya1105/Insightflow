from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, null=True, blank=True, default=None)
    mode = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    user_input = models.TextField()
    response = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.mode} - {self.timestamp}"


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.session_id:
            last_session = ChatSession.objects.order_by('-id').first()
            if last_session and last_session.session_id.startswith('INF'):
                last_number = int(last_session.session_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.session_id = f"INF{new_number:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.session_id} - {self.timestamp}"