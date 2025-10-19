# noticias/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Noticia, Comentario, Categoria

User = get_user_model()


# ----------------------
# Páginas públicas
# ----------------------
def home(request):
    """
    Busca todas as categorias e, para cada uma, separa a notícia mais recente
    como destaque e as seguintes como relacionadas.
    """
    dados_home = []
    # Pega todas as categorias que têm notícias
    categorias = Categoria.objects.filter(noticias__isnull=False).distinct()

    for categoria in categorias:
        # Busca as notícias da categoria atual, ordenadas pela mais recente
        noticias_da_categoria = Noticia.objects.filter(categoria=categoria).order_by('-data_publicacao')
        
        # A primeira da lista é o destaque
        destaque = noticias_da_categoria.first()
        # As próximas 4 são as relacionadas
        relacionadas = noticias_da_categoria[1:5]

        # Adiciona os dados organizados à lista se houver uma notícia de destaque
        if destaque:
            dados_home.append({
                'categoria': categoria,
                'destaque': destaque,
                'relacionadas': relacionadas
            })

    context = {
        'dados_home': dados_home
    }
    
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
    return render(request, "noticia_detalhe.html", {"noticia": noticia})


@require_POST
def adicionar_comentario_ajax(request):
    try:
        noticia_id = int(request.POST.get("noticia_id", ""))
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "Parâmetro noticia_id inválido."}, status=400)

    autor = (request.POST.get("autor") or "").strip()
    texto = (request.POST.get("texto") or "").strip()

    if not autor or not texto:
        return JsonResponse({"ok": False, "error": "Autor e texto são obrigatórios."}, status=400)

    noticia = get_object_or_404(Noticia, pk=noticia_id)
    comentario = Comentario.objects.create(noticia=noticia, autor=autor, texto=texto)

    return JsonResponse(
        {
            "ok": True,
            "comentario": {
                "id": comentario.id,
                "autor": comentario.autor,
                "texto": comentario.texto,
                "data_criacao": comentario.data_criacao.isoformat(),
            },
        }
    )

# ----------------------
# Autenticação
# ----------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso.")
            next_url = request.POST.get("next") or request.GET.get("next") or "home"
            return redirect(next_url)
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("home")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        if not username or not password:
            messages.error(request, "Preencha usuário e senha.")
        elif password != password2:
            messages.error(request, "As senhas não conferem.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Este usuário já existe.")
        else:
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, "Cadastro realizado. Faça login.")
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