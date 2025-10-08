from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================
# Custom User Model
# ==========================
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


# ==========================
# Access Log Model
# ==========================
class AccessLog(models.Model):
    # Importa o modelo de usuário ativo via configuração
    from django.conf import settings
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="access_logs"
    )
    path = models.CharField(max_length=255)   # URL acessada
    action = models.CharField(max_length=255) # tipo de evento
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Anônimo"
        return f"{user_display} - {self.action} em {self.path}"
