from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/", include("apps.authentication.urls")),
    # Tenant management
    path("api/tenants/", include("apps.tenants.urls")),
    # Billing
    path("api/billing/", include("apps.billing.urls")),
    # Core accounting modules
    path("api/accounting/", include("apps.accounting.urls")),
    path("api/invoices/", include("apps.invoicing.urls")),
    path("api/expenses/", include("apps.expenses.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/payroll/", include("apps.payroll.urls")),
    path("api/reports/", include("apps.reports.urls")),
    # Super admin
    path("api/super-admin/", include("apps.super_admin.urls")),
    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar in development
if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
