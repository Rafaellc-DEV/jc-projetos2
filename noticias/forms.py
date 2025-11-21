from django import forms
from .models import PreferenciaEmail, Comentario,CustomUser # Importando Comentario

# ===============================
# Formulário de Preferência de E-mail
# ===============================
class PreferenciaEmailForm(forms.ModelForm):
    class Meta:
        model = PreferenciaEmail
        fields = ['receber_emails', 'categorias']
        widgets = {
            # Transforma a seleção de categorias em Checkboxes fáceis de clicar
            'categorias': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super(PreferenciaEmailForm, self).__init__(*args, **kwargs)
        # Adiciona classe Bootstrap ao checkbox principal
        if 'receber_emails' in self.fields:
            self.fields['receber_emails'].widget.attrs.update({'class': 'form-check-input'})


# ===============================
# NOVO: Formulário de Atualização de E-mail
# ===============================
class AtualizarEmailForm(forms.ModelForm):
    # Sobrescreve o campo email para garantir que o 'type' seja 'email'
    email = forms.EmailField(
        label='Novo Endereço de E-mail',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu novo e-mail'})
    )

    class Meta:
        model = CustomUser
        # O CustomUser é usado porque ele contém o campo 'email'
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica se o novo email já está em uso por outro usuário
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este endereço de e-mail já está sendo usado por outra conta.")
        return email

# ===============================
# Formulário de Comentário (CORRIGIDO)
# ===============================
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        # Inclui apenas o campo 'texto'. Os campos 'noticia' e 'usuario'
        # são preenchidos automaticamente na view.
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escreva seu comentário aqui...'
            }),
        }