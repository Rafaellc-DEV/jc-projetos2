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
    
    # --- PREFERÊNCIAS DE EMAIL (Já existia) ---
    path("preferencias-email/", views.preferencias_email, name="preferencias_email"),
    
    # --- NOVO: ATUALIZAÇÃO DO EMAIL PRINCIPAL ---
    path("atualizar-email/", views.atualizar_email_view, name="atualizar_email"),

    # ----------------------
    # API: Endpoints Específicos
    # ----------------------
    path("api/noticias/<int:id_noticia>/comentarios/", views.CriarComentarioView.as_view(), name="comentarios_api"),
    path("api/noticias/<int:noticia_id>/like/", views.LikeNoticiaView.as_view(), name="like-noticia"),

    # ----------------------
    # Rotas Dinâmicas (Devem ficar por último para não conflitar)
    # ----------------------
    # URL da Categoria
    path("categoria/<slug:categoria_slug>/", views.categoria_detalhe, name="categoria_detalhe"),
    # Detalhe da Notícia (Categoria / Slug da notícia)
    path("<slug:categoria_slug>/<slug:noticia_slug>/", views.noticia_detalhe, name="noticia_detalhe"),

    # ----------------------
    # Inclui rotas do router (API Principal)
    # ----------------------
    path('', include(router.urls)),

    # REMOVIDO: path("", include("noticias.urls")) 
    # MOTIVO: Isso causava um loop infinito (RecursionError) pois o arquivo chamava a si mesmo.
]