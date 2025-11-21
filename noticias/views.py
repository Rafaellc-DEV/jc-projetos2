import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Subquery, OuterRef, Case, When, Value
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.permissions import IsAuthenticated

# --- IMPORTS CORRIGIDOS ---
from .models import Noticia, Comentario, Categoria, Curtida, PreferenciasFeed, PreferenciaEmail
from .forms import PreferenciaEmailForm, AtualizarEmailForm   # Importante: Importar o formulário
from .serializers import ComentarioSerializer, NoticiaSerializer

User = get_user_model()


# ==========================
# FUNÇÃO HELPER (AUXILIAR)
# ==========================
def get_feed_data(categorias_queryset):
    """Busca os dados de Destaque (1) e Relacionadas (4) para um queryset de categorias."""
    dados_home = []
    for categoria in categorias_queryset:
        noticias_da_categoria = Noticia.objects.filter(categoria=categoria).order_by('-data_publicacao')
        
        destaque = noticias_da_categoria.first()
        relacionadas = noticias_da_categoria[1:5]

        if destaque:
            dados_home.append({
                'categoria': categoria,
                'destaque': destaque,
                'relacionadas': relacionadas
            })
    return dados_home

# ==========================
# PÁGINAS PÚBLICAS
# ==========================
def home(request):
    dados_atuais = []
    dados_feed = []
    
    # --- TASK 2: CONTAINER "ATUAIS" ---
    try:
        # 1. Busca primeiro a categoria "Atuais"
        cat_atuais = Categoria.objects.get(slug="atuais")
        noticias_atuais = Noticia.objects.filter(categoria=cat_atuais).order_by('-data_publicacao')
        if noticias_atuais:
            dados_atuais.append({
                'categoria': cat_atuais,
                'destaque': noticias_atuais.first(),
                'relacionadas': noticias_atuais[1:5]
            })
    except Categoria.DoesNotExist:
        pass # Se a categoria "Atuais" não existir, simplesmente não a exibe

    # --- LÓGICA DO FEED (PERSONALIZADO OU PADRÃO) ---
    categorias_para_feed = Categoria.objects.exclude(slug="atuais") # Exclui "Atuais" do feed principal

    if request.user.is_authenticated:
        try:
            preferencias = PreferenciasFeed.objects.get(usuario=request.user)
            if preferencias.personalizacao_ativa and preferencias.categorias_ordenadas:
                ordem_slugs = preferencias.categorias_ordenadas
                preserved_order = Case(*[When(slug=slug, then=Value(i)) for i, slug in enumerate(ordem_slugs)])
                
                categorias_personalizadas = categorias_para_feed.filter(
                    slug__in=ordem_slugs
                ).order_by(preserved_order).distinct()
                
                dados_feed = get_feed_data(categorias_personalizadas)
                
        except PreferenciasFeed.DoesNotExist:
            pass 

    if not dados_feed:
        categorias_padrao = categorias_para_feed.filter(noticias__isnull=False).order_by('ordem', 'nome').distinct()
        dados_feed = get_feed_data(categorias_padrao)

    # Adiciona "Últimas Notícias" no final
    ultimas = Noticia.objects.exclude(categoria__slug="atuais").order_by('-data_publicacao')
    
    # Verifica se preferencias existe antes de usar no if
    user_pref_ativa = False
    if request.user.is_authenticated:
        try:
            pref = PreferenciasFeed.objects.get(usuario=request.user)
            user_pref_ativa = pref.personalizacao_ativa
        except PreferenciasFeed.DoesNotExist:
            pass

    if ultimas and not user_pref_ativa:
        dados_feed.append({
            'categoria': {'nome': 'Últimas Notícias', 'slug': None},
            'destaque': ultimas.first(),
            'relacionadas': ultimas[1:5]
        })

    # --- LÓGICA DA SIDEBAR ---
    sidebar_curtidas = Noticia.objects.annotate(
        num_curtidas=Count('curtidas')
    ).filter(num_curtidas__gt=0).order_by('-num_curtidas')[:5]
    sidebar_recentes = Noticia.objects.all().order_by('-data_publicacao')[:3]

    context = {
        'dados_atuais': dados_atuais,
        'dados_feed': dados_feed,
        'sidebar_curtidas': sidebar_curtidas,
        'sidebar_recentes': sidebar_recentes,
    }
    return render(request, "home.html", context)

@login_required
def personalizar_feed_view(request):
    user = request.user
    preferencias, pref_criada = PreferenciasFeed.objects.get_or_create(usuario=user)
    
    if pref_criada:
        todas_categorias = Categoria.objects.all().order_by('ordem', 'nome').distinct()
        preferencias.categorias_ordenadas = [cat.slug for cat in todas_categorias]
        preferencias.save()

    if request.method == "POST":
        ordem_json = request.POST.get("ordem_categorias")
        if ordem_json:
            preferencias.categorias_ordenadas = json.loads(ordem_json)
        
        preferencias.personalizacao_ativa = request.POST.get("personalizacao_ativa") == "on"
        preferencias.save()
        
        if not user.viu_personalizacao:
            user.viu_personalizacao = True
            user.save()
            
        messages.success(request, "Seu feed foi atualizado com sucesso!")
        return redirect("personalizar_feed")

    slugs_usuario = preferencias.categorias_ordenadas
    # Proteção contra lista vazia ou None
    if not slugs_usuario:
        slugs_usuario = []

    ordem_preservada = Case(*[When(slug=slug, then=Value(i)) for i, slug in enumerate(slugs_usuario)])
    
    categorias_usuario = Categoria.objects.filter(slug__in=slugs_usuario).order_by(ordem_preservada).distinct()
    categorias_disponiveis = Categoria.objects.exclude(slug__in=slugs_usuario).order_by('ordem', 'nome').distinct()

    context = {
        'preferencias': preferencias,
        'categorias_usuario': categorias_usuario,
        'categorias_disponiveis': categorias_disponiveis
    }
    return render(request, "personalizar_feed.html", context)


def categoria_detalhe(request, categoria_slug):
    categoria = get_object_or_404(Categoria, slug=categoria_slug)
    noticias = Noticia.objects.filter(categoria=categoria).order_by('-data_publicacao')
    mais_recentes_sidebar = Noticia.objects.exclude(categoria=categoria).order_by('-data_publicacao')[:5]

    context = {
        'categoria': categoria,
        'noticias': noticias,
        'mais_recentes_sidebar': mais_recentes_sidebar,
    }
    return render(request, "categoria_detalhe.html", context)


def search(request):
    q = request.GET.get("q", "").strip()
    resultados = Noticia.objects.filter(titulo__icontains=q) if q else []
    return render(request, "search.html", {"q": q, "resultados": resultados})

def noticia_detalhe(request, categoria_slug, noticia_slug):
    noticia = get_object_or_404(Noticia, categoria__slug=categoria_slug, slug=noticia_slug)
    noticias_relacionadas = None
    if noticia.categoria:
        noticias_relacionadas = Noticia.objects.filter(
            categoria=noticia.categoria
        ).exclude(pk=noticia.pk).order_by('-data_publicacao')[:4]
    context = {'noticia': noticia, 'noticias_relacionadas': noticias_relacionadas}
    return render(request, "noticia_detalhe.html", context)

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
            
            if not user.viu_personalizacao:
                messages.info(request, "Notei que é seu primeiro acesso. Personalize seu feed!")
                return HttpResponseRedirect(reverse('personalizar_feed')) 
            
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

@login_required
def conteudo_premium(request):
    if getattr(request.user, "user_type", "FREE") != "ASSINANTE":
        return HttpResponseForbidden("Acesso restrito a assinantes.")
    return render(request, "premium.html")

# ==========================
# API VIEWSETS
# ==========================

class NoticiaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Noticia.objects.all().order_by('-data_publicacao')
    serializer_class = NoticiaSerializer

class CriarComentarioView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id_noticia):
        noticia = get_object_or_404(Noticia, id=id_noticia)
        serializer = ComentarioSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(noticia=noticia, usuario=request.user)
            comentario = serializer.instance
            return Response({"ok": True, "comentario": {"id": comentario.id, "autor": comentario.usuario.username, "texto": comentario.texto, "data_criacao": comentario.data_criacao.isoformat(), "pode_apagar": comentario.pode_apagar(request.user)}}, status=status.HTTP_201_CREATED)
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
        return Response({"ok": True, "message": "Comentário excluído."}, status=200)

class LikeNoticiaView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, noticia_id):
        try:
            noticia = get_object_or_404(Noticia, id=noticia_id)
            user = request.user
            curtida = Curtida.objects.filter(usuario=user, noticia=noticia).first()
            if curtida:
                curtida.delete()
                is_curtida = False
                mensagem = "Curtida removida!"
            else:
                Curtida.objects.create(usuario=user, noticia=noticia)
                is_curtida = True
                mensagem = "Curtida adicionada!"
            serializer = NoticiaSerializer(noticia, context={'request': request})
            return Response({'total_curtidas': serializer.data['total_curtidas'], 'is_curtida': is_curtida, 'mensagem': mensagem}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, noticia_id):
        try:
            noticia = get_object_or_404(Noticia, id=noticia_id)
            user = request.user
            curtida = Curtida.objects.filter(usuario=user, noticia=noticia).first()
            if curtida:
                curtida.delete()
                serializer = NoticiaSerializer(noticia, context={'request': request})
                return Response({'total_curtidas': serializer.data['total_curtidas'], 'is_curtida': False, 'mensagem': 'Curtida removida!'}, status=status.HTTP_200_OK)
            return Response({'mensagem': 'Você não curtiu esta notícia.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===============================
# NOVO: View para Atualização de E-mail Principal
# ===============================
@login_required
def atualizar_email_view(request):
    """
    Permite ao usuário autenticado alterar o seu endereço de e-mail principal.
    """
    if request.method == 'POST':
        # Instancia o formulário com a requisição POST e a instância do usuário atual
        form = AtualizarEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            # A função form.save() irá salvar o novo email no objeto CustomUser (request.user)
            form.save()
            messages.success(request, "Seu endereço de e-mail foi atualizado com sucesso!")
            return redirect('atualizar_email') # Redireciona para evitar reenvio
        else:
            # Se o formulário for inválido (ex: email já em uso)
            messages.error(request, "Erro ao atualizar o e-mail. Verifique os dados.")
    else:
        # GET: Carrega o formulário com o e-mail atual do usuário
        form = AtualizarEmailForm(instance=request.user)

    return render(request, 'noticias/atualizar_email.html', {'form': form})

@login_required
def preferencias_email(request):
    # Busca ou cria a preferência do usuário
    preferencia, created = PreferenciaEmail.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Usa o form para validar e salvar os dados
        form = PreferenciaEmailForm(request.POST, instance=preferencia)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferências de e-mail atualizadas com sucesso!")
            return redirect('preferencias_email')
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos.")
    else:
        form = PreferenciaEmailForm(instance=preferencia)

    return render(request, 'preferencias_email.html', {'form': form})
