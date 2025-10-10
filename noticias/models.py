from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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


# ==========================
# Modelo de Notícia
# ==========================
class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo


# ==========================
# Modelo de Comentário
# ==========================
class Comentario(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.CharField(max_length=80)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['data_criacao']

    def __str__(self):
        return f'Comentário de {self.autor} em {self.noticia.titulo[:30]}...'
