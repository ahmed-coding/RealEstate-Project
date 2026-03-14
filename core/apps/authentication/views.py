from django.conf import settings
from django.template import loader
from ..models import generit_random_code
from django.core.mail import send_mail, EmailMessage
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView, Request, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from django.contrib.auth import logout, authenticate, login
from rest_framework.permissions import IsAuthenticated
import firebase_admin
from firebase_admin import firestore

from .serializers import User, UserAuthSerializer, PasswordResetSerializer


class CustomAuthToken(CreateAPIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
                "user_type": user.user_type,
            }
        )


class ReigsterView(CreateAPIView):
    """
    ReigsterAPI to create user if request.session.has_key('email_code') and request.session.has_key('is_verify') is True
    and he will be replace the another view in User.view for Customer at new
    """

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserAuthSerializer

    def post(self, request: Request):
        """
        Reigster User View to signup after verify the ``email`` or ``phone number`` (just email for new).
        Returns:
        - in_Success:
            - data: (``string``) -> message from server.
            - user: (``User``) -> data of user after created.
            - status_code : 200
        - in_Fail:
            - error: (``string``) -> Error Message.
            - status: 401 when come bafore verify the ``email`` or ``phone_number``.
            - status: 400 when data isn't correct or somthing go to by wrong.
        """
        # print(generit_random_code())
        # print(type(generit_random_code()))

        # print(generit_random_code())
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user_data = serializer.validated_data
            # Synchronize user data with Firebase Realtime Database or Firestore
            # db = firestore.client()
            # users_ref = db.collection('Users')
            # users_ref.document(user.id).set({
            #     'email': user_data['email'],
            #     'fullName': user_data.get('name', ''),
            #     'userType' : user_data.get('user_type', ''),
            #     'phone_number': user_data.get('phone_number', ''),
            #     'imageUrl' : user_data.get('image', ''),
            #     # Add other fields as needed
            # }, merge=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    this will be take ``refresh`` token and add it to blackList
    Method :
        >>> [POST]
        dont add more
    """

    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request: Request):
        """
        >>> LOGIN REQUIRD WITH JWT:
        - Try to get Authentication from User it's self by JWT[refresh].
        - then fo get AUTHORIZATION from request[META],

        Returns:
        - data: login done if the logiut success.
        - status: 200 or 401
        """
        # request.auth
        # d = TokenUser(request.auth)
        # d.delete()

        logout(request=request)
        return Response(data={"data": "Logout done"}, status=status.HTTP_200_OK)


#### Email Method ######


@api_view(["POST"])
def check_email_velidate(request: Request):
    """
    Argament:
        `email`: to check email validate.
    """
    # print(dir(request.META))
    # for key in request.META :
    #     print(key)

    if request.data.get("email"):
        try:
            email = User.objects.get(email=request.data.get("email"))
            return Response({"is_valid": False}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"is_valid": True}, status=status.HTTP_200_OK)
    return Response(
        {"error": "check-email-velidate"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def send_verify_email(request: Request):
    """
    Send OTP to email for verification.
    Stores the code in DB with 10-minute expiry - NEVER returns the code in response.
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.models import VerificationCode

    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Generate 4-digit code
        code = generit_random_code(4)

        # Calculate expiry time (10 minutes from now)
        expiry = timezone.now() + timedelta(minutes=10)

        # Delete any existing unused codes for this email
        VerificationCode.objects.filter(email=email, is_used=False).delete()

        # Create new verification code in DB
        VerificationCode.objects.create(
            email=email, random_code=code, expire_date=expiry
        )

        # Send email with the code
        template = loader.get_template("email-template/code_design.html").render(
            {"code": code}
        )
        send = EmailMessage(
            "OTP Form RealEstate authentication Verify",
            template,
            settings.EMAIL_HOST_USER,
            [
                email,
            ],
        )
        send.content_subtype = "html"
        send.send()

        # IMPORTANT: Never return the code in the API response!
        return Response(
            {"message": "Verification code sent to your email"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def verify_email(request: Request):
    """
    Verify the OTP code sent to email.
    Validates against stored code in DB with expiry check.
    """
    from django.utils import timezone
    from apps.models import VerificationCode

    email = request.data.get("email")
    code = request.data.get("code")

    if not email or not code:
        return Response(
            {"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find the verification code for this email
        verification = VerificationCode.objects.filter(
            email=email, random_code=code, is_used=False
        ).first()

        if not verification:
            return Response(
                {"is_valid": False, "error": "Invalid or expired verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if code has expired
        if verification.expire_date < timezone.now():
            return Response(
                {"is_valid": False, "error": "Verification code has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark code as used
        verification.is_used = True
        verification.save()

        return Response(
            {"is_valid": True, "message": "Email verified successfully"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"is_valid": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


#### End Email Method ######


class PasswordResetRequestView(APIView):
    """
    Request a password reset.
    Generates a cryptographic token and sends it via email.
    """

    permission_classes = []  # Public endpoint

    def post(self, request):
        from apps.models import PasswordResetToken
        from django.utils import timezone
        from datetime import timedelta

        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether the email exists or not
            return Response(
                {"message": "If the email exists, a reset link will be sent"},
                status=status.HTTP_200_OK,
            )

        try:
            # Invalidate any existing tokens for this user
            PasswordResetToken.objects.filter(user=user, is_used=False).update(
                is_used=True
            )

            # Generate cryptographically secure token
            token = PasswordResetToken.generate_token()

            # Set expiry to 15 minutes from now
            expire_at = timezone.now() + timedelta(minutes=15)

            # Create token in database
            reset_token = PasswordResetToken.objects.create(
                user=user, token=token, expire_at=expire_at
            )

            # Send email with reset link (containing the token)
            reset_link = f"https://yourdomain.com/reset-password?token={token}"
            template = loader.get_template("email-template/password_reset.html").render(
                {"user": user, "reset_link": reset_link}
            )
            send = EmailMessage(
                "Password Reset Request",
                template,
                settings.EMAIL_HOST_USER,
                [
                    email,
                ],
            )
            send.content_subtype = "html"
            send.send()

            return Response(
                {"message": "If the email exists, a reset link will be sent"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with valid token.
    Validates token, checks expiry, and updates password.
    """

    permission_classes = []  # Public endpoint

    def post(self, request):
        from apps.models import PasswordResetToken
        from django.utils import timezone

        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"error": "Token and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Find the token
            reset_token = (
                PasswordResetToken.objects.filter(token=token, is_used=False)
                .select_related("user")
                .first()
            )

            if not reset_token:
                return Response(
                    {"error": "Invalid or expired reset token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if token has expired
            if reset_token.expire_at < timezone.now():
                return Response(
                    {"error": "Reset token has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate password strength (optional - can add more validation)
            if len(new_password) < 8:
                return Response(
                    {"error": "Password must be at least 8 characters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update password
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Keep old view for backwards compatibility (will be deprecated)
class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer
    permission_classes = []  # Public endpoint

    def post(self, request):
        # This is the old insecure implementation - redirect to new endpoints
        # For backwards compatibility, we'll use the new token-based approach
        from apps.models import PasswordResetToken
        from django.utils import timezone
        from datetime import timedelta

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            new_password = serializer.validated_data.get("new_password")

            # Check if this is a token-based request
            token = request.data.get("token")
            if token:
                # Use the new token-based verification
                reset_token = (
                    PasswordResetToken.objects.filter(token=token, is_used=False)
                    .select_related("user")
                    .first()
                )

                if not reset_token:
                    return Response(
                        {"error": "Invalid or expired reset token"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if reset_token.expire_at < timezone.now():
                    return Response(
                        {"error": "Reset token has expired"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = reset_token.user
                user.set_password(new_password)
                user.save()

                reset_token.is_used = True
                reset_token.save()

                return Response(
                    {"message": "Password has been reset"}, status=status.HTTP_200_OK
                )
            else:
                # Legacy support - just reset without token (insecure, should not be used)
                return Response(
                    {"error": "Token is required for password reset"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
