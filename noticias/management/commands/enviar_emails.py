from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from noticias.models import PreferenciaEmail, EmailSendLog, Noticia


class Command(BaseCommand):
    help = "Envia resumo de notícias por e-mail com base nas preferências de categoria do usuário, em HTML bonitinho."

    def handle(self, *args, **options):
        agora = timezone.now()
        hoje = agora.date()

        # URL base do site – AJUSTA AQUI se mudar o domínio
        SITE_URL = "https://rafaeldev.pythonanywhere.com"
        LOGO_URL = f"{SITE_URL}/static/img/logo.png"
        HERO_URL = LOGO_URL  # se quiser outra imagem de capa, troca aqui

        preferencias = (
            PreferenciaEmail.objects
            .filter(receber_emails=True)
            .select_related("usuario")
            .prefetch_related("categorias")
        )

        if not preferencias.exists():
            self.stdout.write(self.style.WARNING("Nenhum usuário com preferências de e-mail ativas."))
            return

        for pref in preferencias:
            user = pref.usuario

            if not user.email:
                self.stdout.write(
                    self.style.WARNING(f"Usuário {user.username} não tem e-mail cadastrado, pulando.")
                )
                continue

            categorias = pref.categorias.all()

            # Notícias publicadas hoje nas categorias escolhidas
            noticias_qs = (
                Noticia.objects
                .filter(
                    categoria__in=categorias,
                    data_publicacao__date=hoje
                )
                .distinct()
                .order_by("-data_publicacao")
            )

            if not noticias_qs.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Nenhuma notícia para {user.username} nas categorias escolhidas hoje."
                    )
                )
                continue

            # Define destaque + outras (resumo sucinto no template via truncate)
            destaque = noticias_qs.first()
            outras_noticias = noticias_qs[1:5]  # até 4 extras

            subject = f"Resumo das notícias de hoje - {hoje.strftime('%d/%m/%Y')}"

            # Contexto que vai para o template HTML
            context = {
                "user": user,
                "destaque": destaque,
                "outras_noticias": outras_noticias,
                "site_url": SITE_URL,
                "logo_url": LOGO_URL,
                "hero_url": HERO_URL,
                "preferences_link": f"{SITE_URL}/preferencias-email/",
            }

            # Renderiza o HTML
            html_content = render_to_string("emails/newsletter.html", context)

            # Texto simples como fallback
            # (resumo bem direto com "clique aqui para saber mais")
            linhas_texto = [
                f"Olá, {user.first_name or user.username}!\n",
                "Aqui estão as principais notícias selecionadas para você hoje:\n\n",
            ]

            # Destaque
            if destaque:
                linhas_texto.append(f"[DESTAQUE] {destaque.titulo}\n")
                if getattr(destaque, "subtitulo", None):
                    linhas_texto.append(f"{destaque.subtitulo}\n")
                elif getattr(destaque, "conteudo", None):
                    linhas_texto.append(destaque.conteudo[:200] + "...\n")
                linhas_texto.append(
                    f"Clique aqui para saber mais: {SITE_URL}{destaque.get_absolute_url() if hasattr(destaque, 'get_absolute_url') else ''}\n\n"
                )

            # Outras notícias
            for noticia in outras_noticias:
                linhas_texto.append(f"- {noticia.titulo}\n")
                if getattr(noticia, "subtitulo", None):
                    linhas_texto.append(f"{noticia.subtitulo}\n")
                elif getattr(noticia, "conteudo", None):
                    linhas_texto.append(noticia.conteudo[:140] + "...\n")

                link = f"{SITE_URL}{noticia.get_absolute_url()}" if hasattr(noticia, "get_absolute_url") else f"{SITE_URL}/noticia/{noticia.slug}/"
                linhas_texto.append(f"Clique aqui para saber mais: {link}\n\n")

            text_content = "".join(linhas_texto)

            # Monta o e-mail multipart (texto + HTML)
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            # Log do envio
            EmailSendLog.objects.create(
                user=user,
                subject=subject,
                content_preview=text_content[:500],
            )

            self.stdout.write(
                self.style.SUCCESS(f"E-mail HTML enviado com sucesso para {user.email}")
            )

        self.stdout.write(self.style.SUCCESS("Processo de envio de e-mails concluído."))
