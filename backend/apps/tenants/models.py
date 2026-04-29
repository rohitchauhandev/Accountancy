# PUBLIC schema models
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """Each tenant represents one company/organisation on the platform."""

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    auto_create_schema = True

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """Domain linked to a tenant (e.g. acme.yourapp.com)."""

    class Meta:
        ordering = ["-domain"]
