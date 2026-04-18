from django.urls import path
from .views import *

urlpatterns = [
    ### Expense URLs for Account Management
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),

    ### API for category-wise income and expense summary for dashboard cards
    path('category-summary/', CategoryAccountSummaryView.as_view(), name='category-summary'),

    ### Monthly report API (if needed in future)
    path('monthly-report/', MonthlyReportListView.as_view(), name='monthly-report'),

]