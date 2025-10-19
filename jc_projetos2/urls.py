from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # A RAIZ do site deve apontar para as rotas do app 'noticias'
    path('', include('noticias.urls')),
]

# Servir media em DEBUG (para imagens de notícia, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
