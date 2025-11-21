# noticias/admin.py
from django.contrib import admin
from .models import Noticia, Comentario, Categoria, PreferenciaEmail, EmailSendLog

# 1. Registro da Notícia (COM AS ATUALIZAÇÕES PARA O AUTOR)
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Adicionado 'autor', 'imagem' e 'imagem_credito' para aparecer na lista
    list_display = ('titulo', 'autor', 'categoria', 'data_publicacao', 'imagem', 'imagem_credito')
    # Adicionado filtro por categoria e autor
    list_filter = ('categoria', 'autor')
    # Adiciona a barra de pesquisa
    search_fields = ('titulo', 'conteudo')
    # Preenche o slug automaticamente a partir do título
    prepopulated_fields = {'slug': ('titulo',)}

    # Define o autor automaticamente como o usuário logado ao salvar uma nova notícia
    def save_model(self, request, obj, form, change):
        if not obj.autor:
            obj.autor = request.user
        super().save_model(request, obj, form, change)


# 2. Registro do Comentário (Sem alterações)
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'noticia', 'texto', 'data_criacao']  # CORRIGIDO
    list_filter = ['data_criacao', 'noticia']
    search_fields = ['texto', 'usuario__username']

# 3. Registro da Categoria (Sem alterações)
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # O que aparece na lista do painel
    list_display = ('nome',)
    # Adiciona a barra de pesquisa
    search_fields = ('nome',)
    # Preenche o slug automaticamente a partir do nome
    prepopulated_fields = {'slug': ('nome',)}

# 4. Registro da Preferência de Email

# ==========================
# PreferenciaEmail Admin (CORREÇÃO AQUI)
# ==========================
@admin.register(PreferenciaEmail)
class PreferenciaEmailAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'receber_emails', 'criado_em')
    list_filter = ('receber_emails', 'categorias')
    search_fields = ('usuario__username', 'usuario__email')
    # Usa um widget horizontal para a seleção ManyToMany de Categorias
    filter_horizontal = ('categorias',)

    
# 5. Registro do Histórico de Envio

@admin.register(EmailSendLog)
class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('user__username', 'subject', 'content_preview')
    readonly_fields = ('user', 'sent_at', 'subject', 'content_preview')