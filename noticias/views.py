from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model

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
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect(next_url)
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "registration/login.html", {"next": next_url})

def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("home")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # validações simples
        if not username or not password or not password2:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "registration/register.html")

        if password != password2:
            messages.error(request, "As senhas não conferem.")
            return render(request, "registration/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return render(request, "registration/register.html")

        # cria usuário
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect("login")

    return render(request, "registration/register.html")
