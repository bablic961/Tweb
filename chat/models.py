from django.db import models
from django.conf import settings


class Chat(models.Model):
    """Чат между двумя пользователями"""
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chats'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_other_user(self, current_user):
        """Возвращает собеседника"""
        return self.participants.exclude(id=current_user.id).first()

    def __str__(self):
        users = self.participants.all()
        return f"Чат: {', '.join(u.username for u in users)}"


class Message(models.Model):
    """Зашифрованное сообщение"""
    MESSAGE_TYPES = [
        ('text', '💬 Текст'),
        ('image', '🖼 Фото'),
        ('video', '🎬 Видео'),
        ('file', '📎 Файл'),
    ]

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default='text'
    )
    encrypted_text = models.BinaryField(
        null=True,
        blank=True,
        help_text='Зашифрованный текст (AES-256)'
    )
    file = models.FileField(
        upload_to='chat_files/',
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.message_type}"
