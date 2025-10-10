from django.contrib import admin
from .models import Noticia, Comentario 

# 1. Registro da Notícia
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # O que aparece na lista do painel
    list_display = ('titulo', 'data_publicacao')
    # Adiciona a barra de pesquisa
    search_fields = ('titulo', 'conteudo')

# 2. Registro do Comentário
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    # O que aparece na lista do painel
    list_display = ('autor', 'noticia', 'data_criacao')
    # Filtro rápido
    list_filter = ('data_criacao', 'noticia')
    # Permite buscar por autor ou texto
    search_fields = ('autor', 'texto')