from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

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

            # Monta o assunto e o corpo do e-mail
            subject = f"Resumo das notícias de hoje - {hoje.strftime('%d/%m/%Y')}"

            linhas = [
                f"Olá, {user.username}!\n",
                "Aqui está o resumo das notícias de hoje de acordo com as suas preferências:\n",
            ]

            for noticia in noticias:
                linhas.append(f"- {noticia.titulo}\n")
                if hasattr(noticia, "resumo") and noticia.resumo:
                    linhas.append(f"  {noticia.resumo}\n")
                linhas.append("\n")

            message = "".join(linhas)

            # Envia o e-mail
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Registra o envio no log
            EmailSendLog.objects.create(
                user=user,
                subject=subject,
                content_preview=message[:500],
            )

            self.stdout.write(
                self.style.SUCCESS(f"E-mail enviado com sucesso para {user.email}")
            )

        self.stdout.write(self.style.SUCCESS("Processo de envio de e-mails concluído."))
