import uuid
from django.db import models
from students.models import Student

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Conversation")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%b %d, %H:%M')})"

class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ('USER', 'User'),
        ('BOT', 'Bot'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    state = models.CharField(max_length=50, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    missing_information = models.JSONField(default=list, blank=True)
    evidence = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.content[:30]}"
