from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPES = (
        ("FREE", "Free"),
        ("ASSINANTE", "Assinante"),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default="FREE",
    )

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class AccessLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    path = models.CharField(max_length=255)   # URL acessada
    action = models.CharField(max_length=255) # tipo de evento
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.path} - {self.action}"

# Create your models here.
