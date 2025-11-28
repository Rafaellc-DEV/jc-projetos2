from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ----------------------
# Router para DRF ViewSets
# ----------------------
router = DefaultRouter()
router.register(r'api/noticias', views.NoticiaViewSet, basename='noticia')

urlpatterns = [
    # ----------------------
    # Páginas do site
    # ----------------------
    path("", views.home, name="home"),
    path("buscar/", views.search, name="search"),
    
    # Autenticação
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    
    # Funcionalidades de Usuário / Premium
    path("premium/", views.conteudo_premium, name="conteudo_premium"),
    path("personalizar-feed/", views.personalizar_feed_view, name="personalizar_feed"),
    
    # Preferências de e-mail (NEWSLETTER)
    path("preferencias-email/", views.preferencias_email, name="preferencias_email"),
    
    # Atualização do e-mail do usuário
    path("atualizar-email/", views.atualizar_email_view, name="atualizar_email"),

    # ----------------------
    # API: Endpoints Específicos
    # ----------------------
    path("api/noticias/<int:id_noticia>/comentarios/", views.CriarComentarioView.as_view(), name="comentarios_api"),
    path("api/noticias/<int:noticia_id>/like/", views.LikeNoticiaView.as_view(), name="like-noticia"),

    # ----------------------
    # Rotas Dinâmicas IMPORTANTES
    # ----------------------
    
    # URL da Categoria
    path("categoria/<slug:categoria_slug>/", views.categoria_detalhe, name="categoria_detalhe"),
    
    # Detalhe da Notícia
    # ⚠️ Este é o nome certo para usar no reverse() e nos templates
    path("<slug:categoria_slug>/<slug:noticia_slug>/", views.noticia_detalhe, name="noticia_detalhe"),

    # ----------------------
    # Rotas da API REST
    # ----------------------
    path('', include(router.urls)),
]
