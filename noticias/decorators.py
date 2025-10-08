from functools import wraps
from django.shortcuts import redirect
from django.utils import timezone
from .models import AccessLog

def subscriber_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and getattr(user, "user_type", None) == "ASSINANTE":
            return view_func(request, *args, **kwargs)
        try:
            AccessLog.objects.create(
                user=user if user.is_authenticated else None,
                path=request.path,
                action="Tentativa de acesso sem assinatura",
                timestamp=timezone.now(),
            )
        except Exception as e:
            print(f"[subscriber_required] Falha ao registrar log: {e}")
        return redirect("pagina_assinatura")
    return _wrapped_view
