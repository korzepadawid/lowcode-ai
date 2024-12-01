from django.db import models
from django.utils import timezone


class Thread(models.Model):
    uuid = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.uuid


class Message(models.Model):
#    original_input = models.TextField(blank=True)
#    lang = models.CharField(max_length=255)
#    answer_in_lang = models.TextField(blank=True)
    input = models.TextField()
    answer = models.TextField()
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.input

class MessageV2(models.Model):
    input = models.TextField()
    answer = models.TextField()
    thread = models.ForeignKey(Thread, related_name='messagesv2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.input


class Feedback(models.Model):
    message = models.ForeignKey(Message, related_name='feedback', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.value
