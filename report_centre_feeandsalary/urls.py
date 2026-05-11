from django.urls import path
from .views import (
    FeeCollectionReportView,
    SalaryDisbursementReportView,
    FinancialSummaryReportView,
)

urlpatterns = [
    path('reports/fee-collection/', FeeCollectionReportView.as_view(), name='fee-collection-report'),
    path('reports/salary-disbursement/', SalaryDisbursementReportView.as_view(), name='salary-disbursement-report'),
    path('reports/financial-summary/', FinancialSummaryReportView.as_view(), name='financial-summary-report'),
]