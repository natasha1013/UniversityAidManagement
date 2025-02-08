from django.conf import settings
from django.db import models
from django.utils.timezone import now

class Chat(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.sender.username} -> {self.recipient.username}: {self.message}'
    
    class Meta:
        db_table = 'chats'