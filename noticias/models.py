from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify


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
    path = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Anônimo"
        return f"{user_display} - {self.action} em {self.path}"


# ==========================
# Modelo de Categoria
# ==========================
class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

# ==========================
# Modelo de Notícia
# ==========================
class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='noticias')
    
    # --- NOVO CAMPO DE AUTOR ADICIONADO ---
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Se o autor for deletado, a notícia não será.
        null=True, # Permite que o campo seja nulo no banco de dados.
        blank=True, # Permite que o campo seja vazio no admin.
        related_name='noticias_escritas' # Nome para a relação inversa.
    )
    # ------------------------------------

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

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


# ==========================
# Modelo PreferenciasFeed
# ==========================
class PreferenciasFeed(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferencias_feed'
    )
    categorias = models.ManyToManyField(
        Categoria,
        related_name='preferencias_usuarios',
        blank=True
    )
    ordem_categorias = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ordem de prioridade das categorias em formato JSON, ex: {'categoria_id': ordem}"
    )

    def __str__(self):
        return f"Preferências de {self.usuario.username}"

    class Meta:
        verbose_name = "Preferência de Feed"
        verbose_name_plural = "Preferências de Feed"