from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("buscar/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("premium/", views.conteudo_premium, name="conteudo_premium"),
    
    path("<slug:categoria_slug>/<slug:noticia_slug>/", views.noticia_detalhe, name="noticia_detalhe"),
    
    # API DE COMENTÁRIOS
    path("api/noticias/<int:id_noticia>/comentarios/", views.CriarComentarioView.as_view(), name="comentarios_api"),
    
    # NOVA ROTA: APAGAR COMENTÁRIO
    path("api/noticias/<int:id_noticia>/comentarios/delete/", views.CriarComentarioView.as_view(), name="deletar_comentario"),
]