# PUBLIC schema models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.tenants.models import Tenant


# ---------------------------------------------------------------------------
# Role configuration
# ---------------------------------------------------------------------------

ROLE_CHOICES = [
    ('owner', 'Owner'),
    ('admin', 'Admin'),
    ('accountant', 'Accountant'),
    ('viewer', 'Viewer'),
]

ROLE_PERMISSIONS = {
    'owner': [
        'view_all', 'edit_all', 'delete_all',
        'manage_users', 'manage_billing', 'manage_settings',
        'create_invoice', 'create_expense', 'run_payroll',
        'view_reports', 'export_data',
    ],
    'admin': [
        'view_all', 'edit_all',
        'manage_users',
        'create_invoice', 'create_expense', 'run_payroll',
        'view_reports', 'export_data',
    ],
    'accountant': [
        'view_all',
        'create_invoice', 'create_expense',
        'view_reports', 'export_data',
    ],
    'viewer': [
        'view_all',
        'view_reports',
    ],
}


# ---------------------------------------------------------------------------
# Custom manager (email-based auth, no username)
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    """Manager for the custom User model that uses email instead of username."""

    def create_user(self, email, password=None, full_name='', **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, full_name='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'owner')
        extra_fields.setdefault('tenant', None)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, full_name, **extra_fields)


# ---------------------------------------------------------------------------
# Custom User model (public schema)
# ---------------------------------------------------------------------------

class User(AbstractUser):
    """Custom user model for the accounting SaaS platform."""

    username = None  # Remove username, use email instead

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering = ['full_name']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # ------------------------------------------------------------------
    # Permission helpers
    # ------------------------------------------------------------------

    def has_permission(self, permission_name):
        """Check whether the user's role grants a specific permission."""
        return permission_name in ROLE_PERMISSIONS.get(self.role, [])

    def can_edit_financials(self):
        """Return True if the user may edit financial records."""
        return self.role in ['owner', 'admin', 'accountant']

    def can_manage_users(self):
        """Return True if the user may manage other users."""
        return self.role in ['owner', 'admin']

    def can_manage_billing(self):
        """Return True if the user may manage billing/subscription."""
        return self.role == 'owner'

    def get_full_name(self):
        """Return the user's full name."""
        return self.full_name

    def __str__(self):
        return f"{self.full_name} ({self.email})"
