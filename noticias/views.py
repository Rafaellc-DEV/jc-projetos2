from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .decorators import subscriber_required

User = get_user_model()

def home(request):
    return render(request, "home.html")

def search(request):
    q = request.GET.get("q", "").strip()
    results = []  # TODO: implemente a busca real
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
        last_name  = request.POST.get("last_name", "").strip()
        email      = request.POST.get("email", "").strip().lower()
        password   = request.POST.get("password", "")
        password2  = request.POST.get("password2", "")

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

        username = email  # usamos o e-mail como username

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

def conteudo_premium(request):
    """
    View protegida: só assinantes (user_type == 'ASSINANTE') podem ver.
    Se o usuário for FREE, o decorator o redireciona automaticamente
    e registra o acesso no AccessLog.
    """
    return render(request, "premium.html")
