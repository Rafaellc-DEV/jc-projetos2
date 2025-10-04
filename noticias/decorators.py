from functools import wraps
from django.shortcuts import redirect
from .models import AccessLog

def subscriber_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        # Se o usuário é autenticado e assinante
        if user.is_authenticated and getattr(user, "user_type", None) == "ASSINANTE":
            return view_func(request, *args, **kwargs)

        # Registra tentativa de acesso não autorizado
        AccessLog.objects.create(
            user=user if user.is_authenticated else None,
            path=request.path,
            action="Tentativa de acesso sem assinatura"
        )

        # Redireciona para a página de assinatura
        return redirect("pagina_assinatura")  # coloca aqui o nome da url no seu urls.py

    return _wrapped_view
