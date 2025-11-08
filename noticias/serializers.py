# noticias/serializers.py
from rest_framework import serializers
from .models import Noticia, Comentario, Curtida


# ========================
# Curtida Serializer
# ========================
class CurtidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curtida
        fields = ['id', 'usuario', 'noticia', 'data_curtida']
        read_only_fields = ['data_curtida']


# ========================
# Notícia Serializer
# ========================
class NoticiaSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField(read_only=True)
    categoria_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    autor = serializers.StringRelatedField(read_only=True)
    total_curtidas = serializers.SerializerMethodField()
    is_curtida = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'slug', 'conteudo', 'data_publicacao',
            'categoria', 'categoria_id', 'autor', 'imagem',
            'total_curtidas', 'is_curtida'
        ]
        read_only_fields = ['slug', 'data_publicacao', 'autor']

    def get_total_curtidas(self, obj):
        return obj.total_curtidas()

    def get_is_curtida(self, obj):
        user = self.context.get('request').user
        return obj.is_curtida_by_user(user) if user.is_authenticated else False


# ========================
# Comentário Serializer (SEU ORIGINAL + MELHORIAS)
# ========================
class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    pode_apagar = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'noticia', 'usuario', 'texto', 'data_criacao', 'pode_apagar']
        read_only_fields = ['id', 'noticia', 'usuario', 'data_criacao', 'pode_apagar']

    def validate_texto(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("O comentário não pode estar vazio.")
        if len(value) < 3:
            raise serializers.ValidationError("O comentário deve ter pelo menos 3 caracteres.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['usuario'] = request.user
        return super().create(validated_data)

    def get_pode_apagar(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.pode_apagar(request.user)