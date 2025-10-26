from rest_framework import serializers
from .models import Comentario

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

    # NOVO: Mostra se o usuário logado pode apagar
    def get_pode_apagar(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.pode_apagar(request.user)