from django.urls import path
from .views import (
    EmployeeListView,
    SalaryListCreateView,
    SalaryDetailView,
    SalaryApproveView,
    SalaryStatsView,
)

urlpatterns = [
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('salary/', SalaryListCreateView.as_view(), name='salary-list-create'),
    path('salary/stats/', SalaryStatsView.as_view(), name='salary-stats'),
    path('salary/<int:pk>/', SalaryDetailView.as_view(), name='salary-detail'),
    path('salary/<int:pk>/approve/', SalaryApproveView.as_view(), name='salary-approve'),
]