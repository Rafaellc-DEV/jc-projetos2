from django.contrib import admin
from .models import Noticia, Comentario, Categoria

# 1. Registro da Notícia (COM AS ATUALIZAÇÕES PARA O AUTOR)
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Adicionado 'autor' para aparecer na lista
    list_display = ('titulo', 'autor', 'categoria', 'data_publicacao')
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
    # O que aparece na lista do painel
    list_display = ('autor', 'noticia', 'data_criacao')
    # Filtro rápido
    list_filter = ('data_criacao', 'noticia')
    # Permite buscar por autor ou texto
    search_fields = ('autor', 'texto')

# 3. Registro da Categoria (Sem alterações)
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # O que aparece na lista do painel
    list_display = ('nome',)
    # Adiciona a barra de pesquisa
    search_fields = ('nome',)
    # Preenche o slug automaticamente a partir do nome
    prepopulated_fields = {'slug': ('nome',)}