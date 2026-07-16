"""
Autenticação — RF001, RNF001, RNF002, RN015, RN016, RN019.
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings as django_settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from bodiva_app.models import TipoLog, User
from bodiva_app.serializers import EditarPerfilSerializer, RegistoSerializer, UserSerializer, validar_password_rn016
from bodiva_app.services.auditoria import registar_log

token_generator = PasswordResetTokenGenerator()


class RegistoView(generics.CreateAPIView):
    """POST /api/auth/registo/ — Criar nova conta (perfil Investidor por defeito)."""
    queryset = User.objects.all()
    serializer_class = RegistoSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        registar_log(request, utilizador=user, tipo=TipoLog.LOGIN, detalhes="Registo e primeiro login")
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/  { "email": ..., "password": ... }

    Implementação própria (em vez do TokenObtainPairView genérico) para poder
    aplicar o bloqueio de 15 minutos após 5 tentativas falhadas (RN019) e
    registar todas as tentativas nos logs de auditoria (RNF002).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if not email or not password:
            return Response(
                {"detail": "Todos os campos são obrigatórios, por favor preencha o email e a palavra-passe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=email).first()

        # Mensagem genérica quando o utilizador não existe, para não revelar contas registadas (RNF002)
        if not user:
            registar_log(request, tipo=TipoLog.LOGIN_FALHADO, identificador_tentativa=email,
                         detalhes="Email não registado")
            return Response(
                {"detail": "O nome de utilizador/email ou a palavra-passe estão incorrectos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.esta_bloqueado:
            registar_log(request, utilizador=user, tipo=TipoLog.LOGIN_FALHADO, detalhes="Conta bloqueada")
            return Response(
                {"detail": "A sua conta está temporariamente bloqueada devido a múltiplas tentativas "
                           "falhadas, por favor aguarde o tempo restante e tente novamente."},
                status=status.HTTP_423_LOCKED,
            )

        if not user.is_active:
            registar_log(request, utilizador=user, tipo=TipoLog.LOGIN_FALHADO, detalhes="Conta inactiva")
            return Response({"detail": "Esta conta encontra-se inactiva."}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            user.registar_tentativa_falhada()
            registar_log(request, utilizador=user, tipo=TipoLog.LOGIN_FALHADO, detalhes="Palavra-passe incorrecta")
            return Response(
                {"detail": "O nome de utilizador/email ou a palavra-passe estão incorrectos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.limpar_tentativas_falhadas()
        refresh = RefreshToken.for_user(user)
        registar_log(request, utilizador=user, tipo=TipoLog.LOGIN, detalhes="Login bem-sucedido")

        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


class LogoutView(APIView):
    """POST /api/auth/logout/  { "refresh": ... } — invalida o refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            if refresh:
                RefreshToken(refresh).blacklist()
        except TokenError:
            pass
        registar_log(request, utilizador=request.user, tipo=TipoLog.LOGOUT)
        return Response({"detail": "Sessão terminada."}, status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """GET /api/auth/me/ — Perfil do utilizador autenticado. PATCH /api/auth/me/ — editar perfil."""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return EditarPerfilSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        registar_log(request, utilizador=request.user, tipo=TipoLog.GERIR_UTILIZADOR, detalhes="Edição do próprio perfil")
        return Response(UserSerializer(self.get_object()).data)


class PedirRecuperacaoPasswordView(APIView):
    """POST /api/auth/recuperar-password/  { "email": ... }"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        # Resposta idêntica quer o email exista ou não, para não revelar contas (RNF002)
        resposta = {"detail": "Se o email estiver registado, enviámos uma ligação de recuperação."}
        if not user:
            return Response(resposta)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        link = f"{getattr(django_settings, 'FRONTEND_URL', 'http://localhost:5173')}/redefinir-password/{uid}/{token}/"

        send_mail(
            subject="BODIVA Simulador — Recuperação de palavra-passe",
            message=f"Para redefinir a sua palavra-passe, aceda a: {link}\n\nSe não pediu esta recuperação, ignore este email.",
            from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", "no-reply@bodiva-sim.ao"),
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response(resposta)


class ConfirmarRecuperacaoPasswordView(APIView):
    """POST /api/auth/redefinir-password/  { "uid": ..., "token": ..., "nova_password": ... }"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            uid = force_str(urlsafe_base64_decode(request.data.get("uid", "")))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Ligação de recuperação inválida."}, status=status.HTTP_400_BAD_REQUEST)

        token = request.data.get("token", "")
        if not token_generator.check_token(user, token):
            return Response({"detail": "Ligação de recuperação inválida ou expirada."}, status=status.HTTP_400_BAD_REQUEST)

        nova_password = request.data.get("nova_password", "")
        try:
            validar_password_rn016(nova_password, email=user.email, nome=user.first_name)
        except Exception as e:
            detail = e.detail if hasattr(e, "detail") else str(e)
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(nova_password)
        user.limpar_tentativas_falhadas()
        user.save()
        registar_log(request, utilizador=user, tipo=TipoLog.GERIR_UTILIZADOR, detalhes="Redefinição de palavra-passe")
        return Response({"detail": "Palavra-passe redefinida com sucesso."})
