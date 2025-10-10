from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
<<<<<<< Updated upstream
from .decorators import subscriber_required
=======
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Importações para o sistema de comentários
from .models import Noticia, Comentario 
from .forms import ComentarioForm 
>>>>>>> Stashed changes

User = get_user_model()

#
# VIEWS DE NAVEGAÇÃO E AUTENTICAÇÃO
#

def home(request):
    return render(request, "home.html")

def search(request):
    q = request.GET.get("q", "").strip()
    # A linha que deu erro: use apenas espaços normais!
    results = [] # TODO: implemente a busca real
    return render(request, "pesquisa.html", {"q": q, "results": results})

def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "home"
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect(next_url)

        messages.error(request, "E-mail ou senha inválidos.")

    return render(request, "registration/login.html", {"next": next_url})
    
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("home")

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # validações básicas
        if not all([first_name, last_name, email, password, password2]):
            messages.error(request, "Preencha todos os campos.")
            return render(request, "registration/register.html", {
                "first_name": first_name, "last_name": last_name, "email": email
            })

        if "@" not in email or "." not in email.split("@")[-1]:
            messages.error(request, "Informe um e-mail válido.")
            return render(request, "registration/register.html", {
                "first_name": first_name, "last_name": last_name, "email": email
            })

        if password != password2:
            messages.error(request, "As senhas não conferem.")
            return render(request, "registration/register.html", {
                "first_name": first_name, "last_name": last_name, "email": email
            })

        if len(password) < 6:
            messages.error(request, "A senha deve ter pelo menos 6 caracteres.")
            return render(request, "registration/register.html", {
                "first_name": first_name, "last_name": last_name, "email": email
            })

        username = email # usamos o e-mail como username

        if User.objects.filter(username=username).exists():
            messages.error(request, "Já existe uma conta com este e-mail.")
            return render(request, "registration/register.html", {
                "first_name": first_name, "last_name": last_name, "email": email
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Cadastro realizado! Faça login.")
        return redirect("login")

    return render(request, "registration/register.html")

<<<<<<< Updated upstream
def conteudo_premium(request):
    """
    View protegida: só assinantes (user_type == 'ASSINANTE') podem ver.
    Se o usuário for FREE, o decorator o redireciona automaticamente
    e registra o acesso no AccessLog.
    """
    return render(request, "premium.html")
=======
#
# NOVA VIEW: PROCESSAMENTO DE COMENTÁRIOS VIA AJAX
#
@require_POST
def adicionar_comentario_ajax(request):
    # Verificação básica para garantir que é uma requisição AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        form = ComentarioForm(request.POST)
        noticia_id = request.POST.get('noticia_id') # Pega o ID da notícia

        if form.is_valid():
            try:
                # 1. Busca a notícia 
                noticia = get_object_or_404(Noticia, pk=noticia_id)
                
                # 2. Salva o comentário
                comentario = form.save(commit=False)
                comentario.noticia = noticia
                comentario.save()

                return JsonResponse({
                    'sucesso': True, 
                    'mensagem': 'Comentário enviado com sucesso!'
                })
                
            except Noticia.DoesNotExist:
                return JsonResponse({'sucesso': False, 'erros': 'Notícia não encontrada.'})
            
        else:
            # Retorna os erros do formulário (validação)
            return JsonResponse({
                'sucesso': False, 
                'erros': form.errors.as_json()
            })

# No seu views.py

def noticia_detalhe(request, pk):
    # Busca a notícia ou retorna 404
    noticia = get_object_or_404(Noticia, pk=pk)
    
    # Busca todos os comentários associados, ordenados do mais novo para o mais antigo
    comentarios = Comentario.objects.filter(noticia=noticia).order_by('-data_criacao')
    
    # Cria uma instância do formulário de comentário
    form = ComentarioForm() 
    
    context = {
        'noticia': noticia,
        'comentarios': comentarios,
        'form': form, # Passamos o formulário para o template
    }
    
    return render(request, "noticia_detalhe.html", context)

    # Retorno padrão para requisição inválida
    return JsonResponse({'sucesso': False, 'erros': 'Método ou tipo de requisição inválido.'}, status=400)
>>>>>>> Stashed changes
