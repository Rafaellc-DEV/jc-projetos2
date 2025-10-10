from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("buscar/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"), 
<<<<<<< Updated upstream
    path("premium/", views.conteudo_premium, name="conteudo_premium"),
=======
    
    path("noticia/<int:pk>/", views.noticia_detalhe, name="noticia_detalhe"),

    path("comentar/ajax/", views.adicionar_comentario_ajax, name="adicionar_comentario_ajax"),
>>>>>>> Stashed changes
]
# No seu urls.py (do app noticias)
