from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from noticias.models import PreferenciaEmail, EmailSendLog, Noticia


class Command(BaseCommand):
    help = "Envia resumo de notícias por e-mail com base nas preferências de categoria do usuário."

    def handle(self, *args, **options):
        agora = timezone.now()
        hoje = agora.date()

        # Busca todas as preferências onde o usuário marcou que quer receber e-mails
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

            # Filtra notícias pelas categorias de interesse do usuário, publicadas hoje
            noticias = (
                Noticia.objects
                .filter(
                    categoria__in=categorias,
                    data_publicacao__date=hoje
                )
                .distinct()
            )

            if not noticias.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Nenhuma notícia para {user.username} nas categorias escolhidas hoje."
                    )
                )
                continue

            # Assunto do e-mail
            subject = f"Resumo das notícias de hoje - {hoje.strftime('%d/%m/%Y')}"

            # Corpo TEXTO (fallback, caso o cliente de e-mail não suporte HTML)
            linhas = [
                f"Olá, {user.username}!\n",
                "Aqui está o resumo das notícias de hoje de acordo com as suas preferências:\n",
            ]

            for noticia in noticias:
                linhas.append(f"- {noticia.titulo}\n")
                if hasattr(noticia, "resumo") and noticia.resumo:
                    linhas.append(f"  {noticia.resumo}\n")
                linhas.append("\n")

            plain_message = "".join(linhas)

            # Corpo HTML usando template
            context = {
                "user": user,
                "noticias": noticias,
                "hoje": hoje,
                # ajusta para o domínio real quando tiver
                "site_url": "http://127.0.0.1:8000",
                # coloca URL real da logo se tiver
                "logo_url": "https://via.placeholder.com/160x40?text=JC+Online",
                # link para o usuário gerenciar preferências
                "preferences_link": "http://127.0.0.1:8000/preferencias-email/",
            }

            html_body = render_to_string("emails/newsletter.html", context)

            # Monta e-mail multipart (texto + HTML)
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,  # texto simples
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_body, "text/html")

            # Envia o e-mail
            email.send(fail_silently=False)

            # Registra o envio no log
            EmailSendLog.objects.create(
                user=user,
                subject=subject,
                content_preview=plain_message[:500],
            )

            self.stdout.write(
                self.style.SUCCESS(f"E-mail enviado com sucesso para {user.email}")
            )

        self.stdout.write(self.style.SUCCESS("Processo de envio de e-mails concluído."))
