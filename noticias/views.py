# noticias/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Noticia, Comentario, Categoria
from .serializers import ComentarioSerializer

User = get_user_model()


# ----------------------
# Páginas públicas
# ----------------------
def home(request):
    dados_home = []
    categorias = Categoria.objects.filter(noticias__isnull=False).distinct()

    for categoria in categorias:
        noticias_da_categoria = Noticia.objects.filter(categoria=categoria).order_by('-data_publicacao')
        destaque = noticias_da_categoria.first()
        relacionadas = noticias_da_categoria[1:5]

        if destaque:
            dados_home.append({
                'categoria': categoria,
                'destaque': destaque,
                'relacionadas': relacionadas
            })

    context = {'dados_home': dados_home}
    return render(request, "home.html", context)


def search(request):
    q = request.GET.get("q", "").strip()
    resultados = Noticia.objects.filter(titulo__icontains=q) if q else []
    return render(request, "search.html", {"q": q, "resultados": resultados})


# ----------------------
# Notícias e comentários
# ----------------------
def noticia_detalhe(request, categoria_slug, noticia_slug):
    noticia = get_object_or_404(Noticia, categoria__slug=categoria_slug, slug=noticia_slug)
    
    noticias_relacionadas = None
    if noticia.categoria:
        noticias_relacionadas = Noticia.objects.filter(
            categoria=noticia.categoria
        ).exclude(pk=noticia.pk).order_by('-data_publicacao')[:4]

    context = {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas
    }
    return render(request, "noticia_detalhe.html", context)


# ----------------------
# Autenticação
# ----------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        
        if not email or not password:
            messages.error(request, "Por favor, preencha e-mail e senha.")
            return render(request, "registration/login.html")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso.")
            next_url = request.POST.get("next") or request.GET.get("next") or "home"
            return redirect(next_url)
        messages.error(request, "E-mail ou senha inválidos.")
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("home")


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not email or not password:
            messages.error(request, "E-mail e senha são obrigatórios.")
        elif password != password2:
            messages.error(request, "As senhas não conferem.")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
        else:
            User.objects.create_user(
                username=email, 
                email=email, 
                password=password, 
                first_name=first_name, 
                last_name=last_name
            )
            messages.success(request, "Cadastro realizado com sucesso! Faça seu login.")
            return redirect("login")

    return render(request, "registration/register.html")


# ----------------------
# Conteúdo premium
# ----------------------
@login_required
def conteudo_premium(request):
    if getattr(request.user, "user_type", "FREE") != "ASSINANTE":
        return HttpResponseForbidden("Acesso restrito a assinantes.")
    return render(request, "premium.html")


# ----------------------
# API: Comentários (DRF) - POST, GET, DELETE
# ----------------------
class CriarComentarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id_noticia):
        # Busca a notícia
        noticia = get_object_or_404(Noticia, id=id_noticia)

        # Cria o serializer com os dados do POST
        serializer = ComentarioSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Salva com a notícia
            serializer.save(noticia=noticia)
            comentario = serializer.instance  # Pega o comentário salvo
            
            return Response({
                "ok": True,
                "comentario": {
                    "id": comentario.id,
                    "autor": comentario.usuario.username,
                    "texto": comentario.texto,
                    "data_criacao": comentario.data_criacao.isoformat(),
                    "pode_apagar": comentario.pode_apagar(request.user)
                }
            }, status=status.HTTP_201_CREATED)
        else:
            erro = serializer.errors.get('texto', ['Erro ao salvar comentário.'])[0]
            return Response({"ok": False, "error": str(erro)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id_noticia):
        noticia = get_object_or_404(Noticia, id=id_noticia)
        comentarios = noticia.comentarios.all().order_by('-data_criacao')
        
        serializer = ComentarioSerializer(comentarios, many=True, context={'request': request})
        return Response({"ok": True, "comentarios": serializer.data})

    def delete(self, request, id_noticia):
        comentario_id = request.data.get('comentario_id')
        if not comentario_id:
            return Response({"ok": False, "error": "ID do comentário é obrigatório."}, status=400)

        try:
            comentario = Comentario.objects.get(id=comentario_id, noticia_id=id_noticia)
        except Comentario.DoesNotExist:
            return Response({"ok": False, "error": "Comentário não encontrado."}, status=404)

        if not comentario.pode_apagar(request.user):
            return Response({"ok": False, "error": "Você não pode apagar este comentário."}, status=403)

        comentario.delete()
        return Response({"ok": True, "message": "Comentário apagado com sucesso!"}, status=200)