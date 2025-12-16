"""
Salary Management URLs

Route configuration for salary endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SalaryViewSet, SalaryDashboardView

# Create router
router = DefaultRouter()
router.register(r"", SalaryViewSet, basename="salary")

urlpatterns = [
    # Dashboard endpoint (before router to avoid conflict)
    path("dashboard/", SalaryDashboardView.as_view(), name="salary-dashboard"),
    
    # All other salary endpoints via router
    # GET /salary/ - List all salaries
    # POST /salary/ - Create salary
    # GET /salary/{id}/ - Get salary details
    # PUT /salary/{id}/ - Update salary
    # DELETE /salary/{id}/ - Delete salary
    # POST /salary/{id}/pay/ - Process payment
    # POST /salary/bulk-pay/ - Bulk payment
    # GET /salary/export/ - Export to CSV
    # GET /salary/by-employee/{employee_id}/ - Get employee salary history
    # GET /salary/statistics/ - Get statistics
    path("", include(router.urls)),
]
