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
        HERO_URL = LOGO_URL
        
        # ==============================================================================
        # --- CÓDIGO DE MOCK/SIMULAÇÃO DE NOTÍCIAS PARA DEMONSTRAÇÃO ---
        # Estes objetos substituem a consulta ao banco de dados 'Noticia.objects.filter()'.
        
        # Classe simples para simular o objeto Noticia (necessário para o template)
        class SimpleNews:
            def __init__(self, titulo, subtitulo, slug, categoria_slug, conteudo=""):
                self.titulo = titulo
                self.subtitulo = subtitulo
                self.slug = slug
                # Garante que 'conteudo' tem algo para o truncate no template e fallback de texto
                self.conteudo = conteudo or subtitulo 
                # Simula o objeto Categoria com o atributo slug
                self.categoria = type('Categoria', (object,), {'slug': categoria_slug})()
                
            def get_absolute_url(self):
                # Simula a URL completa esperada pelo fallback de texto (necessário para o corpo de texto simples)
                return f"/{self.categoria.slug}/{self.slug}/"

        # Simulação das notícias que seriam obtidas do SITE_URL
        mock_noticias_data = [
            SimpleNews(
                "Lançamento Histórico: Satélite X no Espaço", 
                "A Agência Espacial Brasileira lançou com sucesso o novo satélite de comunicações, superando expectativas.", 
                "lancamento-satelite-x", 
                "ciencia",
                conteudo="Este é o conteúdo longo que seria truncado no e-mail. A missão visa melhorar a conectividade em áreas remotas do país."
            ),
            SimpleNews(
                "Economia: Queda do Dólar Impulsiona Importações", 
                "O mercado reage à nova política monetária e o dólar atinge o menor valor dos últimos 6 meses.", 
                "queda-dolar-importacoes", 
                "economia"
            ),
            SimpleNews(
                "Esportes: Grande Final do Campeonato", 
                "O time favorito vence de virada e leva a taça para casa. Análise completa da partida.", 
                "final-campeonato-futebol", 
                "esportes"
            ),
            SimpleNews(
                "Política: Reforma Administrativa em Discussão", 
                "Deputados debatem as emendas propostas ao texto principal da reforma administrativa.", 
                "reforma-administrativa-debate", 
                "politica"
            ),
        ]
        # --- FIM DO CÓDIGO DE MOCK/SIMULAÇÃO ---
        # ==============================================================================

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
            # Pega os slugs das categorias do usuário para filtrar o mock
            categoria_slugs = [c.slug for c in categorias]

            # ==============================================================================
            # --- SUBSTITUIÇÃO DA CONSULTA AO BANCO DE DADOS PELA SIMULAÇÃO ---
            
            # Filtra as notícias mockadas pelas categorias do usuário
            noticias_selecionadas = [
                n for n in mock_noticias_data 
                # Pega notícias cuja categoria está nas preferências do usuário, ou se o usuário não escolheu categorias
                if n.categoria.slug in categoria_slugs or not categoria_slugs 
            ]
            
            # Renomeia para seguir a variável original, agora é uma lista de SimpleNews
            noticias_qs = noticias_selecionadas 
            
            # --- FIM DA SUBSTITUIÇÃO ---
            # ==============================================================================


            if not noticias_qs: # Mudado .exists() para verificar lista vazia
                self.stdout.write(
                    self.style.WARNING(
                        f"Nenhuma notícia para {user.username} nas categorias escolhidas hoje."
                    )
                )
                continue

            # Define destaque + outras (resumo sucinto no template via truncate)
            destaque = noticias_qs[0]
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
            # O get_absolute_url() da SimpleNews garante que o link funciona aqui também
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
                    f"Clique aqui para saber mais: {SITE_URL}{destaque.get_absolute_url()}\n\n"
                )

            # Outras notícias
            for noticia in outras_noticias:
                linhas_texto.append(f"- {noticia.titulo}\n")
                if getattr(noticia, "subtitulo", None):
                    linhas_texto.append(f"{noticia.subtitulo}\n")
                elif getattr(noticia, "conteudo", None):
                    linhas_texto.append(noticia.conteudo[:140] + "...\n")

                link = f"{SITE_URL}{noticia.get_absolute_url()}"
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