"""
Controlo de acesso baseado em perfis (RBAC) — RNF001.
Dois perfis: Investidor (utilizador comum) e Administrador.
"""
from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """Permite acesso apenas a utilizadores com perfil Administrador."""
    message = "Apenas administradores podem aceder a este recurso."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_administrador
        )


class IsInvestidor(BasePermission):
    """Permite acesso apenas a utilizadores com perfil Investidor."""
    message = "Este recurso está reservado a investidores."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_administrador
        )
