# noticias/models.py
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
    # NOVO CAMPO: Checa se o usuário já viu a tela de personalização
    viu_personalizacao = models.BooleanField(default=False)

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
    
    # --- NOVO CAMPO (REQUEST 1) ---
    # Define a ordem de prioridade no admin (0 = topo)
    ordem = models.IntegerField(
        default=99,
        help_text="Defina a ordem de prioridade (0, 1, 2...). Categorias com números menores aparecem primeiro."
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        # --- NOVA ORDENAÇÃO (REQUEST 1) ---
        ordering = ['ordem', 'nome']


# ==========================
# Modelo de Notícia
# ==========================
class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    subtitulo = models.TextField(
        blank=True, null=True, verbose_name="Sub-título"
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='noticias')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='noticias_escritas'
    )
    imagem = models.ImageField(
        upload_to='noticias_imagens/', 
        blank=True, 
        null=True,
        verbose_name="Imagem de Destaque"
    )

    # --- NOVO CAMPO ADICIONADO ---
    imagem_credito = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Crédito da Imagem"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo

    def total_curtidas(self):
        return self.curtidas.count()

    def is_curtida_by_user(self, user):
        if user.is_authenticated:
            return self.curtidas.filter(usuario=user).exists()
        return False


# ==========================
# Modelo Curtida
# ==========================
class Curtida(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    noticia = models.ForeignKey(
        'Noticia',
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    data_curtida = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'noticia')
        indexes = [
            models.Index(fields=['noticia']),
            models.Index(fields=['usuario']),
        ]

    def __str__(self):
        return f"{self.usuario.username} curtiu {self.noticia.titulo}"


# ==========================
# Modelo Comentario
# ==========================
class Comentario(models.Model):
    noticia = models.ForeignKey('Noticia', on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Comentário de {self.usuario.get_username()} em {self.noticia.titulo[:30]}'

    def pode_apagar(self, user):
        return self.usuario == user


# ==========================
# NOVO MODELO (REQUEST 2)
# ==========================
class PreferenciasFeed(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferencias_feed'
    )
    # Salva uma lista de slugs de categoria na ordem preferida
    # Ex: ["politica", "esportes", "mundo"]
    categorias_ordenadas = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de slugs de categoria na ordem de preferência do usuário."
    )
    # Define se o feed personalizado está ativo ou não
    personalizacao_ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferências de {self.usuario.username}"

    class Meta:
        verbose_name = "Preferência de Feed"
        verbose_name_plural = "Preferências de Feed"