from django.utils import timezone
# from datetime import timezone
from rest_framework import generics, filters, parsers, pagination
from .models import *
from .serializers import *
from account_mm_income.models import account_Income
from django.db.models import Sum, Count
from rest_framework.response import Response


# Custom Pagination (Figma matching 5 entries)
class ExpensePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    pagination_class = ExpensePagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    # Searching and Filtering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voucher_no', 'description', 'expense_category']
    ordering_fields = ['expense_date', 'amount']

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]




#### API for category-wise income and expense summary for dashboard cards
class CategoryAccountSummaryView(generics.ListAPIView):
    serializer_class = CategorySummarySerializer

    def get_queryset(self):
        return []

    def list(self, request, *args, **kwargs):
        income_cats = set(account_Income.objects.values_list('income_category', flat=True).distinct())
        expense_cats = set(Expense.objects.values_list('expense_category', flat=True).distinct())
        
        all_categories = income_cats.union(expense_cats)

        summary_data = []
        grand_total_income = 0
        grand_total_expense = 0

        for cat in all_categories:
            inc_sum = account_Income.objects.filter(income_category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
            
            exp_sum = Expense.objects.filter(expense_category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
            
            balance = inc_sum - exp_sum
            
            summary_data.append({
                "category": cat,
                "total_income": inc_sum,
                "total_expense": exp_sum,
                "remaining_balance": balance
            })
            
            grand_total_income += inc_sum
            grand_total_expense += exp_sum

        serializer = self.get_serializer(summary_data, many=True)
        
        return Response({
            "results": serializer.data,
            "grand_total": {
                "category": "Total",
                "total_income": grand_total_income,
                "total_expense": grand_total_expense,
                "remaining_balance": grand_total_income - grand_total_expense
            }
        })



#### Api for monthly income and expense summary for dashboard cards (if needed in future)
class MonthlyReportListView(generics.ListAPIView):
    queryset = Expense.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            today = timezone.now()
            
            this_month_qs = Expense.objects.filter(
                expense_date__month=today.month, 
                expense_date__year=today.year
            )
            
            stats = this_month_qs.aggregate(
                total_exp=Sum('amount'),
                total_count=Count('id')
            )
            
            largest = this_month_qs.values('expense_category').annotate(
                cat_sum=Sum('amount')
            ).order_by('-cat_sum').first()

            graph_data = []
            for i in range(1, 5):
                start_day = (i-1)*7 + 1
                end_day = i*7
                week_sum = this_month_qs.filter(
                    expense_date__day__range=(start_day, end_day)
                ).aggregate(s=Sum('amount'))['s'] or 0
                
                graph_data.append({
                    "week": f"Week {i}", 
                    "amount": float(week_sum)
                })

            report_data = {
                "summary_cards": {
                    "total_expense": float(stats['total_exp'] or 0),
                    "largest_category": largest['expense_category'] if largest else "N/A",
                    "largest_amount": float(largest['cat_sum'] if largest else 0),
                    "total_entries": stats['total_count'] or 0
                },
                "chart": graph_data
            }

            return Response(report_data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


