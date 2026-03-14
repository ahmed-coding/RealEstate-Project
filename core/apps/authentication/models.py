from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class VerificationCode(models.Model):
    """
    Verification Code model.
    Used to verify accounts with OTP. Stores code in DB with 10-minute expiry.
    """

    email = models.EmailField(_("email"), max_length=254)
    random_code = models.CharField(_("random_code"), max_length=4)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True
    )
    expire_date = models.DateTimeField(
        _("expire_date"), auto_now=False, auto_now_add=False
    )
    is_used = models.BooleanField(_("is_used"), default=False)

    class Meta:
        db_table = "VerificationCode"

    def is_valid(self):
        """Check if the code is still valid (not expired and not used)."""
        from django.utils import timezone

        return not self.is_used and self.expire_date > timezone.now()

    @staticmethod
    def generate_code():
        """Generate a 4-digit code."""
        import random
        import string

        return "".join(random.choices(string.digits, k=4))


class PasswordResetToken(models.Model):
    """
    Password Reset Token model.
    Stores cryptographic tokens for password reset with 15-minute expiry.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(_("token"), max_length=64, unique=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    expire_at = models.DateTimeField(_("expire_at"), auto_now=False, auto_now_add=False)
    is_used = models.BooleanField(_("is_used"), default=False)

    class Meta:
        db_table = "PasswordResetToken"

    def is_valid(self):
        """Check if the token is still valid (not expired and not used)."""
        from django.utils import timezone

        return not self.is_used and self.expire_at > timezone.now()

    @staticmethod
    def generate_token():
        """Generate a cryptographically secure token."""
        import secrets

        return secrets.token_urlsafe(32)
