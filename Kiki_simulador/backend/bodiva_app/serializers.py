import re
from datetime import date
from decimal import Decimal

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import (
    AtivoBodiva,
    Carteira,
    HistoricoInflacao,
    LogAuditoria,
    MovimentoCarteira,
    Perfil,
    PosicaoCarteira,
    ResumoMercado,
    Simulacao,
    User,
)


# ─── Autenticação — RF001, RN016 ─────────────────────────────────────────────

def validar_password_rn016(password, email="", nome=""):
    """
    RN016: mínimo 8 caracteres, com letras e números, e não pode ser igual
    ao email ou ao nome do utilizador.
    """
    if len(password) < 8:
        raise serializers.ValidationError("A palavra-passe deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise serializers.ValidationError("A palavra-passe deve conter letras e números.")
    if email and password.lower() == email.lower():
        raise serializers.ValidationError("A palavra-passe não pode ser igual ao email.")
    if nome and password.lower() == nome.lower():
        raise serializers.ValidationError("A palavra-passe não pode ser igual ao nome.")
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise serializers.ValidationError(list(e.messages))


class RegistoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "phone", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "As palavras-passe não coincidem."})
        validar_password_rn016(data["password"], email=data.get("email", ""), nome=data.get("first_name", ""))
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, perfil=Perfil.INVESTIDOR, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    tem_carteira = serializers.ReadOnlyField()
    is_administrador = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name", "phone",
            "perfil", "tem_carteira", "is_administrador", "created_at",
        ]
        read_only_fields = ["id", "perfil", "created_at"]


class EditarPerfilSerializer(serializers.ModelSerializer):
    password_atual = serializers.CharField(write_only=True, required=False, allow_blank=True)
    nova_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "password_atual", "nova_password"]

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este email já está associado a outro utilizador.")
        return value

    def validate(self, data):
        nova = data.get("nova_password")
        if nova:
            atual = data.get("password_atual")
            if not atual or not self.instance.check_password(atual):
                raise serializers.ValidationError({"password_atual": "A palavra-passe actual está incorrecta."})
            validar_password_rn016(nova, email=data.get("email", self.instance.email), nome=data.get("first_name", ""))
        return data

    def update(self, instance, validated_data):
        nova = validated_data.pop("nova_password", None)
        validated_data.pop("password_atual", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        if nova:
            instance.set_password(nova)
        instance.save()
        return instance


# ─── Carteira — RF002, RN003 ─────────────────────────────────────────────────

class CriarCarteiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carteira
        fields = ["id", "nome", "descricao"]

    def validate_nome(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("O nome da carteira deve ter pelo menos 3 caracteres.")
        return value.strip()

    def create(self, validated_data):
        usuario = self.context["request"].user
        return Carteira.objects.create(usuario=usuario, **validated_data)


class CarteiraSerializer(serializers.ModelSerializer):
    valor_investido = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    valor_atual = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    numero_simulacoes = serializers.ReadOnlyField()

    class Meta:
        model = Carteira
        fields = [
            "id", "nome", "descricao", "valor_investido", "valor_atual",
            "numero_simulacoes", "criada_em", "atualizada_em",
        ]
        read_only_fields = ["id", "criada_em", "atualizada_em"]


# ─── Ativos e preços (ao vivo, a partir de resumo_mercados) — RF008/RF009 ────

class AtivoBodivaSerializer(serializers.ModelSerializer):
    # Estes três já não são colunas na tabela — são lidos ao vivo de
    # resumo_mercados (ver AtivoBodiva.preco_ultimo/variacao_percentual/ultima_atualizacao)
    preco_ultimo = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    variacao_percentual = serializers.DecimalField(max_digits=7, decimal_places=4, read_only=True)
    ultima_atualizacao = serializers.DateField(read_only=True)

    class Meta:
        model = AtivoBodiva
        fields = [
            "id", "ticker", "nome", "tipo", "setor", "isin", "preco_ultimo",
            "variacao_percentual", "ultima_atualizacao", "taxa_juro_nominal",
            "data_maturidade", "valor_nominal", "ativo",
        ]


class ResumoMercadoSerializer(serializers.ModelSerializer):
    """Leitura da série histórica real (tabela resumo_mercados, não-gerida)."""
    # 'preco_fecho' é um alias de 'preco' só para o frontend não ter de mudar de nome de campo.
    preco_fecho = serializers.DecimalField(source="preco", max_digits=16, decimal_places=2, read_only=True)
    data = serializers.DateField(source="data_referencia", read_only=True)

    class Meta:
        model = ResumoMercado
        fields = ["id", "codigo", "mercado", "preco_fecho", "data", "variacao_percentual"]


class InserirPrecoManualSerializer(serializers.Serializer):
    """
    Admin insere manualmente um ponto de preço (RF008) — grava directamente
    em resumo_mercados, a mesma tabela que o scraping externo alimenta.
    """
    data = serializers.DateField()
    preco_fecho = serializers.DecimalField(max_digits=16, decimal_places=2)
    variacao_percentual = serializers.DecimalField(max_digits=7, decimal_places=4, required=False, allow_null=True)

    def validate_data(self, value):
        if value > date.today():
            raise serializers.ValidationError("A data não pode ser futura (dados históricos).")
        return value


# ─── Posições da carteira — RF002/RF003, RN004, RN005 ────────────────────────

class PosicaoCarteiraSerializer(serializers.ModelSerializer):
    ativo = AtivoBodivaSerializer(read_only=True)
    valor_atual = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    custo_total = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    lucro_prejuizo_nominal = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    lucro_prejuizo_percentual = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)

    class Meta:
        model = PosicaoCarteira
        fields = [
            "id", "ativo", "quantidade", "preco_medio", "data_simulada_compra",
            "valor_atual", "custo_total", "lucro_prejuizo_nominal",
            "lucro_prejuizo_percentual", "atualizada_em",
        ]


class AdicionarAtivoSerializer(serializers.Serializer):
    """RF002/RN004/RN005 — adicionar um activo à carteira, a um preço histórico."""
    ativo_id = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=20, decimal_places=4, min_value=Decimal("0.0001"))
    data_simulada_compra = serializers.DateField()

    def validate_data_simulada_compra(self, value):
        if value > date.today():
            raise serializers.ValidationError("A data da compra simulada não pode ser futura.")
        return value

    def validate_ativo_id(self, value):
        if not AtivoBodiva.objects.filter(pk=value, ativo=True).exists():
            raise serializers.ValidationError("Ativo inexistente ou indisponível.")
        return value


class MovimentoCarteiraSerializer(serializers.ModelSerializer):
    ativo_ticker = serializers.CharField(source="ativo.ticker", read_only=True)

    class Meta:
        model = MovimentoCarteira
        fields = [
            "id", "ativo", "ativo_ticker", "tipo", "quantidade",
            "preco_unitario", "valor_total", "data_simulada", "executado_em",
        ]


# ─── Inflação — RF009, RN008 ─────────────────────────────────────────────────

class HistoricoInflacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoInflacao
        fields = ["id", "ano", "mes", "ipc_mensal", "fonte", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_mes(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("O mês deve estar entre 1 e 12.")
        return value


# ─── Simulações — RF004/RF005/RF006/RF007 ────────────────────────────────────

class SimulacaoInputSerializer(serializers.Serializer):
    """RN017 — validação de entrada: valor positivo, período válido, ativo existente."""
    ativo_id = serializers.IntegerField()
    valor_investido = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    data_inicio = serializers.DateField()
    data_fim = serializers.DateField()

    def validate_ativo_id(self, value):
        if not AtivoBodiva.objects.filter(pk=value, ativo=True).exists():
            raise serializers.ValidationError("Ativo inexistente ou indisponível para simulação.")
        return value

    def validate(self, data):
        if data["data_inicio"] >= data["data_fim"]:
            raise serializers.ValidationError("A data de início deve ser anterior à data de fim.")
        if data["data_fim"] > date.today():
            raise serializers.ValidationError("A data de fim não pode ser uma data futura.")
        return data


class SimulacaoSerializer(serializers.ModelSerializer):
    ativo = AtivoBodivaSerializer(read_only=True)

    class Meta:
        model = Simulacao
        fields = [
            "id", "ativo", "valor_investido", "data_inicio", "data_fim",
            "preco_inicio", "preco_fim", "rentabilidade_nominal_pct",
            "inflacao_acumulada_pct", "rentabilidade_real_pct",
            "valor_final_nominal", "valor_final_real",
            "lucro_prejuizo_nominal", "criada_em",
        ]
        read_only_fields = fields


# ─── Auditoria — RF015, CSU-009 ──────────────────────────────────────────────

class LogAuditoriaSerializer(serializers.ModelSerializer):
    utilizador_email = serializers.CharField(source="utilizador.email", read_only=True, default=None)

    class Meta:
        model = LogAuditoria
        fields = [
            "id", "tipo", "utilizador", "utilizador_email", "identificador_tentativa",
            "detalhes", "endereco_ip", "criado_em",
        ]


# ─── Administração de utilizadores — CSU-006 ─────────────────────────────────

class GerirUtilizadorSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    tem_carteira = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name", "perfil",
            "estado", "bloqueado_pelo_admin", "tem_carteira", "date_joined", "created_at",
        ]

    def get_estado(self, obj):
        return "bloqueado" if obj.esta_bloqueado else "ativo"
