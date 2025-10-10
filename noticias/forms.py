# Arquivo: [SeuApp]/forms.py

from django import forms
from .models import Comentario # Garante que você está importando o modelo de Comentário

class ComentarioForm(forms.ModelForm):
    """
    Define o formulário para coletar o nome e o texto do comentário.
    """
    class Meta:
        model = Comentario
        # Os campos que o usuário preenche no modal
        fields = ('autor', 'texto')
        
        # Estilização básica com Bootstrap
        widgets = {
            'autor': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Seu nome ou apelido'
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Digite seu comentário...'
            }),
        }