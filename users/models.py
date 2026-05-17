from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True
    )
    bio = models.CharField(max_length=100, blank=True, default='')
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class ContactNickname(models.Model):
    """Локальные подписи контактов"""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nicknames'
    )
    contact = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nicknamed_by'
    )
    nickname = models.CharField(max_length=50)

    class Meta:
        unique_together = ('owner', 'contact')

    def __str__(self):
        return f"{self.owner} называет {self.contact} как '{self.nickname}'"