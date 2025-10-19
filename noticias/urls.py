
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("buscar/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("premium/", views.conteudo_premium, name="conteudo_premium"),
    
    # Rota de detalhe da notícia atualizada
    path("<slug:categoria_slug>/<slug:noticia_slug>/", views.noticia_detalhe, name="noticia_detalhe"),
    
    path("comentar/ajax/", views.adicionar_comentario_ajax, name="adicionar_comentario_ajax"),
]