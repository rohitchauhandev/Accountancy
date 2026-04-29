# PUBLIC schema models
from datetime import date

from django.db import models
from django.utils import timezone
from django_tenants.models import DomainMixin, TenantMixin


# ---------------------------------------------------------------------------
# Plan configuration
# ---------------------------------------------------------------------------

PLAN_CHOICES = [
    ('free', 'Free'),
    ('starter', 'Starter'),
    ('pro', 'Pro'),
    ('business', 'Business'),
]

PLAN_LIMITS = {
    'free':     {'users': 1,  'companies': 1,    'invoices': 25,   'expenses': 50},
    'starter':  {'users': 3,  'companies': 2,    'invoices': 100,  'expenses': 200},
    'pro':      {'users': 5,  'companies': 5,    'invoices': 9999, 'expenses': 9999},
    'business': {'users': 15, 'companies': 9999, 'invoices': 9999, 'expenses': 9999},
}


# ---------------------------------------------------------------------------
# Tenant (public schema)
# ---------------------------------------------------------------------------

class Tenant(TenantMixin):
    """Each tenant represents one company/organisation on the platform."""

    name = models.CharField(max_length=255)
    owner_email = models.EmailField()
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')

    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)

    trial_ends_at = models.DateTimeField(null=True, blank=True)

    # Monthly usage counters
    invoice_count_this_month = models.PositiveIntegerField(default=0)
    expense_count_this_month = models.PositiveIntegerField(default=0)
    invoice_reset_date = models.DateField(default=date.today)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    auto_create_schema = True

    class Meta:
        ordering = ['-created_at']

    # ------------------------------------------------------------------
    # Plan helpers
    # ------------------------------------------------------------------

    def get_plan_limits(self):
        """Return the limits dict for the tenant's current plan."""
        return PLAN_LIMITS[self.plan]

    def can_create_invoice(self):
        """Check whether the tenant can create another invoice this month."""
        limits = self.get_plan_limits()
        return self.invoice_count_this_month < limits['invoices']

    def can_create_expense(self):
        """Check whether the tenant can create another expense this month."""
        limits = self.get_plan_limits()
        return self.expense_count_this_month < limits['expenses']

    def can_add_user(self, current_user_count):
        """Check whether the tenant can add another user."""
        limits = self.get_plan_limits()
        return current_user_count < limits['users']

    def can_add_company(self, current_company_count):
        """Check whether the tenant can add another company."""
        limits = self.get_plan_limits()
        return current_company_count < limits['companies']

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def reset_monthly_counters(self):
        """Reset invoice/expense counts and set the next reset date."""
        self.invoice_count_this_month = 0
        self.expense_count_this_month = 0
        today = date.today()
        if today.month == 12:
            self.invoice_reset_date = date(today.year + 1, 1, 1)
        else:
            self.invoice_reset_date = date(today.year, today.month + 1, 1)
        self.save(update_fields=[
            'invoice_count_this_month',
            'expense_count_this_month',
            'invoice_reset_date',
        ])

    def is_on_trial(self):
        """Return True if the tenant is still within its trial period."""
        return self.trial_ends_at and timezone.now() < self.trial_ends_at

    def upgrade_plan(self, new_plan):
        """Upgrade (or change) the tenant's plan."""
        self.plan = new_plan
        self.save(update_fields=['plan'])

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Domain (public schema)
# ---------------------------------------------------------------------------

class Domain(DomainMixin):
    """Domain linked to a tenant (e.g. acme.yourapp.com)."""

    def __str__(self):
        return self.domain


# ---------------------------------------------------------------------------
# App lists for settings (SHARED_APPS / TENANT_APPS)
# ---------------------------------------------------------------------------

SHARED_APPS = [
    'django_tenants',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_celery_beat',
    'django_filters',
    'drf_spectacular',
    'apps.tenants',
    'apps.authentication',
    'apps.billing',
    'apps.super_admin',
]

TENANT_APPS = [
    'django.contrib.contenttypes',
    'apps.accounting',
    'apps.invoicing',
    'apps.expenses',
    'apps.inventory',
    'apps.payroll',
    'apps.reports',
]
