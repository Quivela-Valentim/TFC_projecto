"""
Serviço de Auditoria — RF015, RNF002, RN019.

Centraliza o registo de logs para garantir que todas as acções relevantes
(login, criação/eliminação de carteira, simulações, gestão administrativa)
ficam registadas de forma consistente, sem nunca guardar dados sensíveis.
"""
from bodiva_app.models import LogAuditoria, TipoLog


def obter_ip(request):
    """Extrai o endereço IP do pedido, considerando proxies (X-Forwarded-For)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def registar_log(request=None, utilizador=None, tipo=TipoLog.LOGIN, detalhes="", identificador_tentativa=""):
    """
    Cria uma entrada de auditoria.
    'request' é opcional (usado para capturar o IP); pode ser omitido em
    contextos internos como comandos de gestão.
    """
    LogAuditoria.objects.create(
        utilizador=utilizador,
        identificador_tentativa=identificador_tentativa,
        tipo=tipo,
        detalhes=detalhes,
        endereco_ip=obter_ip(request) if request is not None else None,
    )
