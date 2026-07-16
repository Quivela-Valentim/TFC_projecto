from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# ─── Utilizador e Autenticação (RF001, RNF001, RN015, RN016, RN019) ──────────

class Perfil(models.TextChoices):
    INVESTIDOR = "INVESTIDOR", "Investidor"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"


class User(AbstractUser):
    """Utilizador do sistema. O perfil determina o dashboard e as permissões (RBAC)."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.INVESTIDOR)

    # RN019 — bloqueio temporário após tentativas de login falhadas
    tentativas_login_falhadas = models.PositiveSmallIntegerField(default=0)
    bloqueado_ate = models.DateTimeField(null=True, blank=True)

    # Bloqueio administrativo manual (CSU-006), distinto do bloqueio automático por tentativas
    bloqueado_pelo_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Redeclarados só para dar um nome curto à tabela de ligação (não usamos
    # grupos/permissões do Django para RBAC — isso é feito pelo campo 'perfil').
    groups = models.ManyToManyField(
        "auth.Group", verbose_name="grupos", blank=True,
        related_name="bodiva_user_set", db_table="utilizadores_grupos",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", verbose_name="permissões", blank=True,
        related_name="bodiva_user_permissions_set", db_table="utilizadores_permissoes",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "utilizadores"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"

    def __str__(self):
        return self.email

    @property
    def tem_carteira(self):
        return hasattr(self, "carteira")

    @property
    def is_administrador(self):
        return self.perfil == Perfil.ADMINISTRADOR or self.is_superuser

    @property
    def esta_bloqueado(self):
        """Bloqueio activo: manual (admin) OU temporário por tentativas falhadas (RN019)."""
        if self.bloqueado_pelo_admin:
            return True
        if self.bloqueado_ate and timezone.now() < self.bloqueado_ate:
            return True
        return False

    def registar_tentativa_falhada(self):
        self.tentativas_login_falhadas += 1
        if self.tentativas_login_falhadas >= 5:
            self.bloqueado_ate = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=["tentativas_login_falhadas", "bloqueado_ate"])

    def limpar_tentativas_falhadas(self):
        if self.tentativas_login_falhadas or self.bloqueado_ate:
            self.tentativas_login_falhadas = 0
            self.bloqueado_ate = None
            self.save(update_fields=["tentativas_login_falhadas", "bloqueado_ate"])


# ─── Carteira Fictícia — RN003 (única por investidor), RF002 ─────────────────

class Carteira(models.Model):
    """
    Carteira fictícia. RN003: cada investidor pode criar apenas UMA carteira —
    imposto ao nível da base de dados via OneToOneField (não apenas na aplicação).
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carteira"
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carteiras"
        verbose_name = "Carteira"
        verbose_name_plural = "Carteiras"

    def __str__(self):
        return f"{self.nome} ({self.usuario.email})"

    @property
    def valor_investido(self):
        """Soma do valor investido (custo de aquisição) de todas as posições activas."""
        total = Decimal("0.00")
        for posicao in self.posicoes.filter(quantidade__gt=0):
            total += posicao.custo_total
        return total

    @property
    def valor_atual(self):
        """Soma do valor de mercado actual das posições, ao último preço conhecido."""
        total = Decimal("0.00")
        for posicao in self.posicoes.filter(quantidade__gt=0):
            total += posicao.valor_atual
        return total

    @property
    def numero_simulacoes(self):
        return self.simulacoes.count()


# ─── Activos BODIVA — RF008, RN005 ───────────────────────────────────────────

class TipoAtivo(models.TextChoices):
    ACAO = "ACAO", "Ação"
    OBRIGACAO_TESOURO = "OT", "Obrigação do Tesouro"
    BILHETE_TESOURO = "BT", "Bilhete do Tesouro"


class AtivoBodiva(models.Model):
    """
    Catálogo de metadados de um ativo (nome comercial, tipo, ISIN, taxa de
    cupão, maturidade). O preço em si NÃO fica guardado aqui — vem sempre,
    ao vivo, da tabela real 'resumo_mercados' (ver ResumoMercado), para
    nunca haver uma cópia desactualizada dos dados de mercado.
    """

    ticker = models.CharField(max_length=50, unique=True, help_text="Corresponde ao 'codigo' em resumo_mercados/livros_de_ordens")
    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TipoAtivo.choices)
    setor = models.CharField(max_length=100, blank=True)
    isin = models.CharField(max_length=12, blank=True)

    # Campos específicos de OT/BT
    taxa_juro_nominal = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True,
        help_text="Taxa de juro anual nominal (%)",
    )
    data_maturidade = models.DateField(null=True, blank=True)
    valor_nominal = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ativos"
        verbose_name = "Ativo BODIVA"
        verbose_name_plural = "Ativos BODIVA"
        ordering = ["ticker"]

    def __str__(self):
        return f"{self.ticker} — {self.nome}"

    def _ultimo_resumo(self):
        return ResumoMercado.objects.filter(codigo=self.ticker).order_by("-data_referencia").first()

    @property
    def preco_ultimo(self):
        r = self._ultimo_resumo()
        return r.preco if r else None

    @property
    def variacao_percentual(self):
        r = self._ultimo_resumo()
        return r.variacao_percentual if r else None

    @property
    def ultima_atualizacao(self):
        r = self._ultimo_resumo()
        return r.data_referencia if r else None

    def preco_em(self, data):
        """
        Preço de fecho mais recente até à data pedida (inclusive), lido ao
        vivo de 'resumo_mercados'. RN006/RN007 dependem deste valor.
        """
        registo = ResumoMercado.objects.filter(codigo=self.ticker, data_referencia__lte=data).order_by("-data_referencia").first()
        return registo.preco if registo else None

    def historico_precos(self):
        """Série histórica completa (para gráficos, RF010), ao vivo."""
        return ResumoMercado.objects.filter(codigo=self.ticker).order_by("data_referencia")


class ResumoMercado(models.Model):
    """
    Mapeamento directo (não-gerido) da tabela real 'resumo_mercados', criada
    e alimentada pelo próprio utilizador fora do Django (scraping manual da
    BODIVA). O Django nunca cria, altera nem apaga esta tabela — apenas lê e,
    quando o administrador insere um preço manualmente pelo painel, escreve
    também aqui, exactamente como o scraper do utilizador faria.
    """
    codigo = models.CharField(max_length=50)
    mercado = models.CharField(max_length=50)
    preco = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    variacao_percentual = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    num_negocios = models.IntegerField()
    volume = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    data_referencia = models.DateField()

    class Meta:
        managed = False
        db_table = "resumo_mercados"
        verbose_name = "Resumo de Mercado (tabela externa)"
        verbose_name_plural = "Resumo de Mercado (tabela externa)"
        unique_together = [("codigo", "data_referencia")]
        ordering = ["codigo", "data_referencia"]

    def __str__(self):
        return f"{self.codigo} — {self.data_referencia}: {self.preco}"


class LivroDeOrdens(models.Model):
    """
    Mapeamento directo (não-gerido) da tabela real 'livros_de_ordens' do
    utilizador. Usada para enriquecer o catálogo (ISIN, taxa de cupão,
    maturidade) — ver comando 'sincronizar_ativos'.
    """
    codigo = models.CharField(max_length=20)
    isin = models.CharField(max_length=12, null=True, blank=True)
    tipologia = models.CharField(max_length=30)
    dividendos = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    taxa_de_cupao = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    data_de_emissao = models.DateField(null=True, blank=True)
    data_de_vencimento = models.DateField(null=True, blank=True)
    ultima_cotacao = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    quantidade_de_compra = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    preco_de_compra = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    yield_compra = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    quantidade_de_venda = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    preco_de_venda = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    yield_venda = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    data_referencia = models.DateField()

    class Meta:
        managed = False
        db_table = "livros_de_ordens"
        verbose_name = "Livro de Ordens (tabela externa)"
        verbose_name_plural = "Livros de Ordens (tabela externa)"
        unique_together = [("codigo", "data_referencia")]
        ordering = ["codigo", "data_referencia"]

    def __str__(self):
        return f"{self.codigo} — {self.data_referencia}"


# ─── Posições da Carteira — RF002/RF003, RN004 ───────────────────────────────

class PosicaoCarteira(models.Model):
    """
    Activo fictício adicionado à carteira. A compra é registada a um preço
    histórico ('data_simulada'), nunca a um preço em tempo real (RN001/RN004).
    """
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name="posicoes")
    ativo = models.ForeignKey(AtivoBodiva, on_delete=models.PROTECT, related_name="posicoes")
    quantidade = models.DecimalField(
        max_digits=20, decimal_places=4, validators=[MinValueValidator(Decimal("0"))]
    )
    preco_medio = models.DecimalField(
        max_digits=20, decimal_places=4, help_text="Preço médio de aquisição (na data simulada)"
    )
    data_simulada_compra = models.DateField(help_text="Data histórica usada como referência da compra")
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posicoes"
        verbose_name = "Posição na Carteira"
        verbose_name_plural = "Posições na Carteira"
        unique_together = [("carteira", "ativo")]

    def __str__(self):
        return f"{self.carteira.nome} — {self.ativo.ticker} ({self.quantidade})"

    @property
    def valor_atual(self):
        preco = self.ativo.preco_ultimo or self.preco_medio
        return self.quantidade * preco

    @property
    def custo_total(self):
        return self.quantidade * self.preco_medio

    @property
    def lucro_prejuizo_nominal(self):
        return self.valor_atual - self.custo_total

    @property
    def lucro_prejuizo_percentual(self):
        if self.custo_total == 0:
            return Decimal("0.00")
        return (self.lucro_prejuizo_nominal / self.custo_total) * 100


class TipoMovimento(models.TextChoices):
    ADICAO = "ADICAO", "Adição de ativo"
    REMOCAO = "REMOCAO", "Remoção de ativo"


class MovimentoCarteira(models.Model):
    """Registo histórico de adições/remoções de ativos na carteira (para auditoria e extrato)."""
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name="movimentos")
    ativo = models.ForeignKey(AtivoBodiva, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=TipoMovimento.choices)
    quantidade = models.DecimalField(max_digits=20, decimal_places=4)
    preco_unitario = models.DecimalField(max_digits=20, decimal_places=4)
    valor_total = models.DecimalField(max_digits=20, decimal_places=2)
    data_simulada = models.DateField()
    executado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimentos"
        verbose_name = "Movimento de Carteira"
        verbose_name_plural = "Movimentos de Carteira"
        ordering = ["-executado_em"]

    def __str__(self):
        return f"{self.tipo} {self.quantidade}x {self.ativo.ticker} ({self.executado_em:%Y-%m-%d})"


# ─── Inflação — RF009, RN008 ─────────────────────────────────────────────────

class HistoricoInflacao(models.Model):
    """IPC mensal de Angola, usado no ajuste da rentabilidade real (RN007/RN008/RN009)."""
    ano = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    ipc_mensal = models.DecimalField(
        max_digits=8, decimal_places=4, help_text="Variação percentual mensal do IPC (%)"
    )
    fonte = models.CharField(max_length=100, default="INE Angola")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inflacao"
        verbose_name = "Histórico de Inflação"
        verbose_name_plural = "Histórico de Inflação"
        ordering = ["-ano", "-mes"]
        unique_together = [("ano", "mes")]

    def __str__(self):
        return f"IPC {self.mes:02d}/{self.ano}: {self.ipc_mensal}%"


# ─── Simulações — RF004/RF005/RF006/RF007, RN006/RN007/RN008/RN011/RN012/RN013 ──

class Simulacao(models.Model):
    """
    Simulação retrospectiva de investimento: o investidor define montante,
    activo e período (data início/fim); o sistema calcula a rentabilidade
    nominal e real ajustada à inflação, sem alterar dados reais (RF006).
    """
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name="simulacoes")
    ativo = models.ForeignKey(AtivoBodiva, on_delete=models.PROTECT, related_name="simulacoes")

    valor_investido = models.DecimalField(max_digits=20, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    preco_inicio = models.DecimalField(max_digits=20, decimal_places=4)
    preco_fim = models.DecimalField(max_digits=20, decimal_places=4)

    rentabilidade_nominal_pct = models.DecimalField(max_digits=10, decimal_places=4)
    inflacao_acumulada_pct = models.DecimalField(max_digits=10, decimal_places=4)
    rentabilidade_real_pct = models.DecimalField(max_digits=10, decimal_places=4)

    valor_final_nominal = models.DecimalField(max_digits=20, decimal_places=2)
    valor_final_real = models.DecimalField(max_digits=20, decimal_places=2)
    lucro_prejuizo_nominal = models.DecimalField(max_digits=20, decimal_places=2)

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "simulacoes"
        verbose_name = "Simulação"
        verbose_name_plural = "Simulações"
        ordering = ["-criada_em"]

    def __str__(self):
        return f"Simulação {self.ativo.ticker} {self.data_inicio}→{self.data_fim} ({self.criada_em:%Y-%m-%d})"


# ─── Auditoria — RF015, RNF002, RN019 ────────────────────────────────────────

class TipoLog(models.TextChoices):
    LOGIN = "LOGIN", "Login bem-sucedido"
    LOGIN_FALHADO = "LOGIN_FALHADO", "Tentativa de login falhada"
    LOGOUT = "LOGOUT", "Logout"
    CRIAR_CARTEIRA = "CRIAR_CARTEIRA", "Criação de carteira"
    ADICIONAR_ATIVO = "ADICIONAR_ATIVO", "Adição de ativo à carteira"
    REMOVER_ATIVO = "REMOVER_ATIVO", "Remoção de ativo da carteira"
    SIMULACAO = "SIMULACAO", "Simulação de investimento"
    GERIR_UTILIZADOR = "GERIR_UTILIZADOR", "Gestão de utilizador"
    GERIR_INFLACAO = "GERIR_INFLACAO", "Gestão de taxa de inflação"
    GERIR_ATIVO = "GERIR_ATIVO", "Gestão de ativo/dados financeiros"
    CONSULTA_LOGS = "CONSULTA_LOGS", "Consulta de logs"
    CONSULTA_DADOS_FINANCEIROS = "CONSULTA_DADOS_FINANCEIROS", "Consulta de dados financeiros"


class LogAuditoria(models.Model):
    """Log de auditoria (RN019, CSU-009). Nunca regista dados sensíveis como palavras-passe."""
    utilizador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs"
    )
    identificador_tentativa = models.CharField(
        max_length=255, blank=True,
        help_text="Email usado numa tentativa de login falhada, quando o utilizador não é identificável",
    )
    tipo = models.CharField(max_length=30, choices=TipoLog.choices)
    detalhes = models.TextField(blank=True)
    endereco_ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logs"
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ["-criado_em"]

    def __str__(self):
        quem = self.utilizador.email if self.utilizador else (self.identificador_tentativa or "desconhecido")
        return f"[{self.tipo}] {quem} — {self.criado_em:%Y-%m-%d %H:%M}"