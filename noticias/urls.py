# noticias/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ----------------------
# Router para DRF ViewSets
# ----------------------
router = DefaultRouter()
router.register(r'api/noticias', views.NoticiaViewSet, basename='noticia')  # GET list + detail com curtidas

urlpatterns = [
    # ----------------------
    # Páginas do site
    # ----------------------
    path("", views.home, name="home"),
    path("buscar/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("premium/", views.conteudo_premium, name="conteudo_premium"),
    
    path("<slug:categoria_slug>/<slug:noticia_slug>/", views.noticia_detalhe, name="noticia_detalhe"),
    
    # ----------------------
    # API: Comentários (POST, GET, DELETE)
    # ----------------------
    path("api/noticias/<int:id_noticia>/comentarios/", views.CriarComentarioView.as_view(), name="comentarios_api"),
    
    # ----------------------
    # API: Curtidas (POST = curtir/descurtir, DELETE = descurtir)
    # ----------------------
    path("api/noticias/<int:noticia_id>/like/", views.LikeNoticiaView.as_view(), name="like-noticia"),
    
    # ----------------------
    # Inclui rotas do router
    # ----------------------
    path('', include(router.urls)),
]